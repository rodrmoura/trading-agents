import test from "node:test";
import assert from "node:assert/strict";

import { createGatewayController, createVsCodeModelService } from "../dist/index.js";
import { requestSse, sendRawHttpRequest } from "./sseTestClient.mjs";

const MAX_CHAT_BODY_BYTES = 1024 * 1024;

function streamUrl(status) {
  return `http://${status.host}:${status.port}/v1/chat/completions/stream`;
}

function buildChatBody(overrides = {}) {
  return {
    model: "model-alpha",
    messages: [{ role: "user", content: "Hello" }],
    ...overrides,
  };
}

function getBearerToken(gateway) {
  const token = gateway.getToken();
  assert.ok(token);
  return token;
}

async function postStream(gateway, body, contentType = "application/json") {
  const status = gateway.getStatus();
  const token = getBearerToken(gateway);

  return fetch(streamUrl(status), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": contentType,
    },
    body: typeof body === "string" ? body : JSON.stringify(body),
  });
}

function withTimeout(promise, timeoutMs, message) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error(message));
      }, timeoutMs);
    }),
  ]);
}

test("stream requires bearer auth before body parsing or model access", async () => {
  let startChatCalls = 0;

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async startChat() {
        startChatCalls += 1;
        throw new Error("should-not-run");
      },
      async completeChat() {
        return "unused";
      },
    },
  });

  await gateway.start();

  try {
    const status = gateway.getStatus();
    const unauthorized = await fetch(streamUrl(status), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: "{not-json",
    });

    assert.equal(unauthorized.status, 401);
    const body = await unauthorized.json();
    assert.equal(body.error.code, "unauthorized");
    assert.equal(startChatCalls, 0);
  } finally {
    await gateway.stop("command");
  }
});

test("stream enforces and accepts JSON content-type variants", async () => {
  let startChatCalls = 0;

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async startChat() {
        startChatCalls += 1;
        return {
          text: (async function* createChunks() {
            yield "ok";
          })(),
          dispose() {},
        };
      },
      async completeChat() {
        return "unused";
      },
    },
  });

  await gateway.start();

  try {
    const status = gateway.getStatus();
    const token = getBearerToken(gateway);
    const acceptedTypes = ["application/json", "application/json; charset=utf-8", "APPLICATION/JSON"];

    for (const contentType of acceptedTypes) {
      const response = await requestSse({
        status,
        token,
        body: buildChatBody(),
        headers: {
          "Content-Type": contentType,
        },
      });

      assert.equal(response.statusCode, 200);
      assert.equal(String(response.headers["content-type"]).startsWith("text/event-stream"), true);
      assert.deepEqual(
        response.events.map((event) => event.event),
        ["chunk", "done"]
      );
    }

    assert.equal(startChatCalls, acceptedTypes.length);

    const missingContentType = await sendRawHttpRequest({
      status,
      token,
      headers: {},
      chunks: [JSON.stringify(buildChatBody())],
    });

    assert.equal(missingContentType.statusCode, 415);
    assert.equal(String(missingContentType.headers["content-type"]).startsWith("application/json"), true);
    assert.equal(JSON.parse(missingContentType.bodyText).error.code, "unsupported_media_type");
    assert.equal(missingContentType.bodyText.includes("event:"), false);

    const wrongContentType = await postStream(gateway, buildChatBody(), "text/plain");
    assert.equal(wrongContentType.status, 415);
    assert.equal(wrongContentType.headers.get("content-type")?.startsWith("application/json"), true);
    assert.equal((await wrongContentType.json()).error.code, "unsupported_media_type");

    assert.equal(startChatCalls, acceptedTypes.length);
  } finally {
    await gateway.stop("command");
  }
});

test("stream rejects malformed JSON, empty body, and oversized body", async () => {
  let startChatCalls = 0;

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async startChat() {
        startChatCalls += 1;
        return {
          text: (async function* createChunks() {
            yield "ok";
          })(),
          dispose() {},
        };
      },
      async completeChat() {
        return "unused";
      },
    },
  });

  await gateway.start();

  try {
    const status = gateway.getStatus();
    const token = getBearerToken(gateway);

    const malformed = await postStream(gateway, "{\"model\":", "application/json");
    assert.equal(malformed.status, 400);
    assert.equal(malformed.headers.get("content-type")?.startsWith("application/json"), true);
    assert.equal((await malformed.json()).error.code, "invalid_json");

    const empty = await sendRawHttpRequest({
      status,
      token,
      headers: {
        "Content-Type": "application/json",
      },
      chunks: [],
    });

    assert.equal(empty.statusCode, 400);
    assert.equal(JSON.parse(empty.bodyText).error.code, "invalid_json");

    const oversizedByLength = await postStream(gateway, "x".repeat(MAX_CHAT_BODY_BYTES + 1), "application/json");
    assert.equal(oversizedByLength.status, 400);
    assert.equal((await oversizedByLength.json()).error.code, "validation_error");

    const oversizedByChunk = await sendRawHttpRequest({
      status,
      token,
      headers: {
        "Content-Type": "application/json",
      },
      chunks: ["x".repeat(MAX_CHAT_BODY_BYTES + 512)],
    });

    assert.equal(oversizedByChunk.statusCode, 400);
    assert.equal(JSON.parse(oversizedByChunk.bodyText).error.code, "validation_error");
    assert.equal(startChatCalls, 0);
  } finally {
    await gateway.stop("command");
  }
});

test("stream rejects unknown top-level and message fields", async () => {
  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async startChat() {
        throw new Error("should-not-run");
      },
      async completeChat() {
        return "unused";
      },
    },
  });

  await gateway.start();

  try {
    const invalidTopLevel = [
      { stream: true },
      { temperature: 0.2 },
      { tools: [] },
      { tool_choice: "auto" },
      { response_format: { type: "json_object" } },
      { extra: 1 },
    ];

    for (const addition of invalidTopLevel) {
      const response = await postStream(gateway, { ...buildChatBody(), ...addition });
      assert.equal(response.status, 400);
      assert.equal((await response.json()).error.code, "validation_error");
    }

    const invalidMessageName = await postStream(gateway, {
      model: "model-alpha",
      messages: [{ role: "user", content: "Hello", name: "alice" }],
    });
    assert.equal(invalidMessageName.status, 400);
    assert.equal((await invalidMessageName.json()).error.code, "validation_error");

    const invalidMessageToolCalls = await postStream(gateway, {
      model: "model-alpha",
      messages: [{ role: "assistant", content: "tool", tool_calls: [] }],
    });
    assert.equal(invalidMessageToolCalls.status, 400);
    assert.equal((await invalidMessageToolCalls.json()).error.code, "validation_error");
  } finally {
    await gateway.stop("command");
  }
});

test("stream validation/startup failures before headers return JSON native errors", async () => {
  const startupScenarios = [
    { thrownError: { code: "NotFound" }, expectedStatus: 404, expectedCode: "model_not_found" },
    { thrownError: { code: "NoPermissions" }, expectedStatus: 403, expectedCode: "model_access_denied" },
    { thrownError: { code: "Blocked" }, expectedStatus: 429, expectedCode: "quota_or_rate_limited" },
  ];

  for (const scenario of startupScenarios) {
    const gateway = createGatewayController({
      modelService: {
        async listModels() {
          return [];
        },
        async startChat() {
          throw scenario.thrownError;
        },
        async completeChat() {
          return "unused";
        },
      },
    });

    await gateway.start();

    try {
      const response = await postStream(gateway, buildChatBody());
      assert.equal(response.status, scenario.expectedStatus);
      assert.equal(response.headers.get("content-type")?.startsWith("application/json"), true);
      const body = await response.json();
      assert.equal(body.error.code, scenario.expectedCode);
      assert.equal(JSON.stringify(body).includes("event:"), false);
    } finally {
      await gateway.stop("command");
    }
  }
});

test("stream emits SSE chunk order and done payload without OpenAI DONE sentinel", async () => {
  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async startChat() {
        return {
          text: (async function* createChunks() {
            yield "First ";
            yield "second";
            yield " third";
          })(),
          dispose() {},
        };
      },
      async completeChat() {
        return "unused";
      },
    },
  });

  await gateway.start();

  try {
    const status = gateway.getStatus();
    const token = getBearerToken(gateway);
    const requestModel = "Opaque Id With Spaces / Do-Not-Normalize";

    const response = await requestSse({
      status,
      token,
      body: {
        model: requestModel,
        messages: [{ role: "user", content: "hello" }],
      },
    });

    assert.equal(response.statusCode, 200);
    assert.equal(String(response.headers["content-type"]).startsWith("text/event-stream"), true);

    assert.deepEqual(
      response.events.map((event) => event.event),
      ["chunk", "chunk", "chunk", "done"]
    );

    assert.deepEqual(
      response.events.filter((event) => event.event === "chunk").map((event) => event.data.text),
      ["First ", "second", " third"]
    );

    const doneEvent = response.events.find((event) => event.event === "done");
    assert.ok(doneEvent);
    assert.equal(doneEvent.data.id.startsWith("gwchat_"), true);
    assert.equal(doneEvent.data.model, requestModel);
    assert.equal(doneEvent.data.finishReason, "stop");
    assert.deepEqual(doneEvent.data.metadata, {});

    assert.equal(response.bodyText.includes("[DONE]"), false);
    assert.equal(response.bodyText.includes("event: chunk\ndata: {\"text\":\"First \"}\n\n"), true);
  } finally {
    await gateway.stop("command");
  }
});

test("stream skips empty chunks but preserves whitespace-only chunks", async () => {
  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async startChat() {
        return {
          text: (async function* createChunks() {
            yield "";
            yield " ";
            yield "\n";
            yield "";
            yield "ok";
          })(),
          dispose() {},
        };
      },
      async completeChat() {
        return "unused";
      },
    },
  });

  await gateway.start();

  try {
    const status = gateway.getStatus();
    const token = getBearerToken(gateway);

    const response = await requestSse({
      status,
      token,
      body: buildChatBody(),
    });

    assert.equal(response.statusCode, 200);

    const chunkTexts = response.events
      .filter((event) => event.event === "chunk")
      .map((event) => event.data.text);

    assert.deepEqual(chunkTexts, [" ", "\n", "ok"]);
  } finally {
    await gateway.stop("command");
  }
});

test("stream iteration failures after headers emit one sanitized SSE error event", async () => {
  const secretPrompt = "PROMPT_SECRET_123";
  const secretResponse = "RESPONSE_SECRET_456";

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async startChat() {
        return {
          text: (async function* createChunks() {
            yield "partial";
            throw new Error(`provider details ${secretResponse}`);
          })(),
          dispose() {},
        };
      },
      async completeChat() {
        return "unused";
      },
    },
  });

  await gateway.start();

  try {
    const status = gateway.getStatus();
    const token = getBearerToken(gateway);

    const response = await requestSse({
      status,
      token,
      body: {
        model: "model-alpha",
        messages: [{ role: "user", content: secretPrompt }],
      },
    });

    assert.equal(response.statusCode, 200);

    const errorEvents = response.events.filter((event) => event.event === "error");
    assert.equal(errorEvents.length, 1);
    assert.equal(errorEvents[0].data.error.code, "unknown_model_error");
    assert.equal(errorEvents[0].data.error.message, "The model request failed.");

    const serialized = JSON.stringify(errorEvents[0].data);
    assert.equal(serialized.includes(secretPrompt), false);
    assert.equal(serialized.includes(secretResponse), false);

    assert.deepEqual(
      response.events.map((event) => event.event),
      ["chunk", "error"]
    );
  } finally {
    await gateway.stop("command");
  }
});

test("stream cancellation-like failures after headers emit cancelled SSE error", async () => {
  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async startChat() {
        return {
          text: (async function* createChunks() {
            yield "partial";
            throw { code: "CancelledByClient" };
          })(),
          dispose() {},
        };
      },
      async completeChat() {
        return "unused";
      },
    },
  });

  await gateway.start();

  try {
    const status = gateway.getStatus();
    const token = getBearerToken(gateway);

    const response = await requestSse({
      status,
      token,
      body: buildChatBody(),
    });

    assert.equal(response.statusCode, 200);

    const errorEvents = response.events.filter((event) => event.event === "error");
    assert.equal(errorEvents.length, 1);
    assert.equal(errorEvents[0].data.error.code, "cancelled");
    assert.equal(errorEvents[0].data.error.message, "The request was cancelled.");
  } finally {
    await gateway.stop("command");
  }
});

test("stream client disconnect aborts model cancellation token/source", async () => {
  let tokenAbortResolver;
  const tokenAborted = new Promise((resolve) => {
    tokenAbortResolver = resolve;
  });

  let sendRequestCalls = 0;

  const modelService = createVsCodeModelService(
    {
      async selectChatModels(selector) {
        assert.deepEqual(selector, {});
        return [
          {
            id: "model-alpha",
            name: "Model Alpha",
            async sendRequest(_messages, _options, token) {
              sendRequestCalls += 1;

              const waitForAbort = new Promise((resolve) => {
                if (token.aborted) {
                  tokenAbortResolver();
                  resolve();
                  return;
                }

                token.addEventListener(
                  "abort",
                  () => {
                    tokenAbortResolver();
                    resolve();
                  },
                  { once: true }
                );
              });

              return {
                text: (async function* createChunks() {
                  yield "first";
                  await waitForAbort;
                  throw { code: "CancelledByDisconnect" };
                })(),
              };
            },
          },
        ];
      },
    },
    {
      createUserMessage(content) {
        return { role: "user", content };
      },
      createAssistantMessage(content) {
        return { role: "assistant", content };
      },
      createCancellationSource() {
        const controller = new AbortController();
        return {
          token: controller.signal,
          cancel() {
            controller.abort();
          },
          dispose() {},
        };
      },
    }
  );

  const gateway = createGatewayController({ modelService });
  await gateway.start();

  try {
    const status = gateway.getStatus();
    const token = getBearerToken(gateway);

    const responsePromise = requestSse({
      status,
      token,
      body: buildChatBody(),
      destroyOnEvent(event) {
        return event.event === "chunk";
      },
    });

    await withTimeout(tokenAborted, 2000, "Model cancellation token was not aborted after disconnect.");

    const response = await withTimeout(responsePromise, 2000, "Destroyed stream request did not settle.");
    assert.equal(response.requestDestroyed, true);
    assert.equal(sendRequestCalls, 1);
  } finally {
    await gateway.stop("command");
  }
});

test("gateway stop aborts active stream and stop resolves", async () => {
  let startedResolver;
  const started = new Promise((resolve) => {
    startedResolver = resolve;
  });

  let abortedResolver;
  const aborted = new Promise((resolve) => {
    abortedResolver = resolve;
  });

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async startChat(_request, signal) {
        const waitForAbort = new Promise((resolve) => {
          if (signal.aborted) {
            abortedResolver();
            resolve();
            return;
          }

          signal.addEventListener(
            "abort",
            () => {
              abortedResolver();
              resolve();
            },
            { once: true }
          );
        });

        return {
          text: (async function* createChunks() {
            startedResolver();
            await waitForAbort;
            throw { code: "CancelledByStop" };
          })(),
          dispose() {},
        };
      },
      async completeChat() {
        return "unused";
      },
    },
  });

  await gateway.start();

  try {
    const status = gateway.getStatus();
    const token = getBearerToken(gateway);

    const streamPromise = requestSse({
      status,
      token,
      body: buildChatBody(),
      headers: {
        Connection: "close",
      },
      agent: false,
    });

    await withTimeout(started, 2000, "Stream request did not start.");

    const stopResult = await withTimeout(gateway.stop("command"), 2000, "Gateway stop did not resolve.");
    assert.equal(stopResult.outcome, "stopped");

    await withTimeout(aborted, 2000, "Active stream was not aborted during stop.");

    const settledStream = await withTimeout(streamPromise, 2000, "Stream request did not settle after stop.");
    assert.ok(settledStream.closed || settledStream.ended || settledStream.requestDestroyed);
  } finally {
    await gateway.stop("command");
  }
});
