import http from "node:http";

function createSseParser(onEvent) {
  let buffered = "";
  let eventName = null;
  let dataLines = [];

  const emitEvent = () => {
    if (eventName === null && dataLines.length === 0) {
      return;
    }

    const rawData = dataLines.join("\n");
    let parsedData = rawData;

    if (rawData.length > 0) {
      try {
        parsedData = JSON.parse(rawData);
      } catch {
        parsedData = rawData;
      }
    }

    onEvent({
      event: eventName ?? "message",
      data: parsedData,
      rawData,
    });

    eventName = null;
    dataLines = [];
  };

  const parseLine = (line) => {
    if (line.length === 0) {
      emitEvent();
      return;
    }

    if (line.startsWith("event:")) {
      eventName = line.slice("event:".length).trimStart();
      return;
    }

    if (line.startsWith("data:")) {
      let value = line.slice("data:".length);
      if (value.startsWith(" ")) {
        value = value.slice(1);
      }

      dataLines.push(value);
    }
  };

  return {
    push(chunkText) {
      buffered += chunkText;

      while (true) {
        const newlineIndex = buffered.indexOf("\n");
        if (newlineIndex < 0) {
          break;
        }

        let line = buffered.slice(0, newlineIndex);
        buffered = buffered.slice(newlineIndex + 1);

        if (line.endsWith("\r")) {
          line = line.slice(0, -1);
        }

        parseLine(line);
      }
    },
    finish() {
      if (buffered.length > 0) {
        let line = buffered;
        buffered = "";

        if (line.endsWith("\r")) {
          line = line.slice(0, -1);
        }

        parseLine(line);
      }

      emitEvent();
    },
  };
}

export async function sendRawHttpRequest(options) {
  const {
    status,
    token,
    path = "/v1/chat/completions/stream",
    method = "POST",
    headers = {},
    chunks = [],
    ignoreRequestErrors = false,
  } = options;

  return new Promise((resolve, reject) => {
    const request = http.request(
      {
        host: status.host,
        port: status.port,
        method,
        path,
        headers: {
          ...headers,
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      },
      (response) => {
        const responseChunks = [];

        response.on("data", (chunk) => {
          responseChunks.push(Buffer.from(chunk));
        });

        response.on("end", () => {
          resolve({
            statusCode: response.statusCode ?? 0,
            headers: response.headers,
            bodyText: Buffer.concat(responseChunks).toString("utf8"),
          });
        });
      }
    );

    request.on("error", (error) => {
      if (ignoreRequestErrors) {
        resolve({ statusCode: 0, headers: {}, bodyText: "", error });
        return;
      }

      reject(error);
    });

    for (const chunk of chunks) {
      request.write(chunk);
    }

    request.end();
  });
}

export async function requestSse(options) {
  const {
    status,
    token,
    body,
    path = "/v1/chat/completions/stream",
    method = "POST",
    headers = {},
    destroyOnEvent,
    agent,
  } = options;

  const result = {
    statusCode: 0,
    headers: {},
    bodyText: "",
    events: [],
    ended: false,
    closed: false,
    requestDestroyed: false,
    requestError: null,
    responseError: null,
  };

  return new Promise((resolve, reject) => {
    let settled = false;

    const settle = () => {
      if (settled) {
        return;
      }

      settled = true;
      resolve(result);
    };

    const requestHeaders = {
      ...headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    const hasBody = body !== undefined;
    if (
      hasBody &&
      requestHeaders["Content-Type"] === undefined &&
      requestHeaders["content-type"] === undefined
    ) {
      requestHeaders["Content-Type"] = "application/json";
    }

    const request = http.request(
      {
        host: status.host,
        port: status.port,
        method,
        path,
        agent,
        headers: requestHeaders,
      },
      (response) => {
        result.statusCode = response.statusCode ?? 0;
        result.headers = response.headers;

        const parser = createSseParser((event) => {
          result.events.push(event);

          if (destroyOnEvent && destroyOnEvent(event, result.events)) {
            result.requestDestroyed = true;
            request.destroy();
          }
        });

        response.on("data", (chunk) => {
          const text = Buffer.from(chunk).toString("utf8");
          result.bodyText += text;
          parser.push(text);
        });

        response.on("end", () => {
          parser.finish();
          result.ended = true;
          settle();
        });

        response.on("close", () => {
          if (result.ended) {
            return;
          }

          parser.finish();
          result.closed = true;
          settle();
        });

        response.on("error", (error) => {
          result.responseError = error;
          settle();
        });
      }
    );

    request.on("error", (error) => {
      if (request.destroyed) {
        result.requestDestroyed = true;
        result.requestError = error;
        settle();
        return;
      }

      reject(error);
    });

    if (hasBody) {
      const bodyText = typeof body === "string" ? body : JSON.stringify(body);
      request.write(bodyText);
    }

    request.end();
  });
}
