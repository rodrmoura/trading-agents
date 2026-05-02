import test from "node:test";
import assert from "node:assert/strict";
import { Server } from "node:http";

import {
  createGatewayController,
  createVsCodeModelService,
  mapLanguageModelErrorCode,
  buildCopyTokenResult,
  buildStatusMessage,
  buildStartMessage,
  buildStopMessage,
} from "../dist/index.js";

function healthUrl(status) {
  return `http://${status.host}:${status.port}/health`;
}

function shutdownUrl(status) {
  return `http://${status.host}:${status.port}/shutdown`;
}

function modelsUrl(status) {
  return `http://${status.host}:${status.port}/v1/models`;
}

function chatUrl(status) {
  return `http://${status.host}:${status.port}/v1/chat/completions`;
}

function streamUrl(status) {
  return `http://${status.host}:${status.port}/v1/chat/completions/stream`;
}

async function fetchAuthorizedModels(gateway) {
  const status = gateway.getStatus();
  const token = gateway.getToken();
  assert.ok(token);

  return fetch(modelsUrl(status), {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

test("start binds to 127.0.0.1 and token is generated after running", async () => {
  const gateway = createGatewayController();

  const startResult = await gateway.start();
  assert.equal(startResult.outcome, "started");
  assert.equal(startResult.status.state, "running");
  assert.equal(startResult.status.host, "127.0.0.1");
  assert.equal(typeof startResult.status.port, "number");
  assert.ok(startResult.status.port > 0);
  assert.ok(startResult.status.startedAt);

  const token = gateway.getToken();
  assert.equal(typeof token, "string");
  assert.ok(token.length > 0);

  const stopResult = await gateway.stop("command");
  assert.equal(stopResult.outcome, "stopped");
  assert.equal(stopResult.status.state, "stopped");
  assert.equal(gateway.getToken(), null);
});

test("start while running is idempotent and does not rotate token", async () => {
  const gateway = createGatewayController();

  const started = await gateway.start();
  assert.equal(started.status.state, "running");
  const token = gateway.getToken();
  assert.ok(token);

  const secondStart = await gateway.start();
  assert.equal(secondStart.outcome, "already_running");
  assert.equal(secondStart.status.state, "running");
  assert.equal(gateway.getToken(), token);

  const stopResult = await gateway.stop("command");
  assert.equal(stopResult.outcome, "stopped");
});

test("stop while stopped is safe and returns already_stopped", async () => {
  const gateway = createGatewayController();

  const stopResult = await gateway.stop("command");
  assert.equal(stopResult.outcome, "already_stopped");
  assert.equal(stopResult.status.state, "stopped");
  assert.equal(gateway.getToken(), null);
});

test("failed start after bind closes local server handle", async () => {
  const gateway = createGatewayController();

  const originalAddress = Server.prototype.address;
  const originalClose = Server.prototype.close;
  let closesWhileListening = 0;

  Server.prototype.address = function patchedAddress() {
    return "unsupported-address-format";
  };

  Server.prototype.close = function patchedClose(callback) {
    if (this.listening) {
      closesWhileListening += 1;
    }

    return originalClose.call(this, callback);
  };

  try {
    const startResult = await gateway.start();
    assert.equal(startResult.outcome, "failed");
    assert.equal(startResult.status.state, "stopped");
    assert.equal(gateway.getStatus().state, "stopped");
    assert.equal(gateway.getToken(), null);
    assert.ok(closesWhileListening > 0);
  } finally {
    Server.prototype.address = originalAddress;
    Server.prototype.close = originalClose;
  }
});

test("public /health has expected shape and never includes token", async () => {
  const gateway = createGatewayController();
  await gateway.start();
  const status = gateway.getStatus();

  const response = await fetch(healthUrl(status));
  assert.equal(response.status, 200);
  const body = await response.json();

  assert.equal(body.status, "ok");
  assert.equal(body.version, "0.0.1");
  assert.equal(body.host, "127.0.0.1");
  assert.equal(typeof body.port, "number");
  assert.equal(typeof body.startedAt, "string");
  assert.equal(body.auth, "bearer");
  assert.equal(Object.prototype.hasOwnProperty.call(body, "token"), false);

  await gateway.stop("command");
});

test("/shutdown requires bearer auth", async () => {
  const gateway = createGatewayController();
  await gateway.start();
  const status = gateway.getStatus();

  const unauthorizedResponse = await fetch(shutdownUrl(status), {
    method: "POST",
  });
  assert.equal(unauthorizedResponse.status, 401);
  const unauthorizedBody = await unauthorizedResponse.json();
  assert.equal(unauthorizedBody.error.code, "unauthorized");

  await gateway.stop("command");
});

test("/shutdown sends response before closing and clears token via shared stop path", async () => {
  const gateway = createGatewayController();
  await gateway.start();
  const status = gateway.getStatus();
  const token = gateway.getToken();
  assert.ok(token);

  const response = await fetch(shutdownUrl(status), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  assert.equal(response.status, 200);
  const responseBody = await response.json();
  assert.equal(responseBody.ok, true);

  const waitUntilStopped = async () => {
    for (let attempt = 0; attempt < 50; attempt += 1) {
      if (gateway.getStatus().state === "stopped") {
        return;
      }

      await new Promise((resolve) => setTimeout(resolve, 10));
    }

    assert.fail("Gateway did not stop after authenticated shutdown.");
  };

  await waitUntilStopped();
  assert.equal(gateway.getToken(), null);
});

test("protected endpoint auth gating and method handling", async () => {
  const gateway = createGatewayController();
  await gateway.start();
  const status = gateway.getStatus();
  const token = gateway.getToken();
  assert.ok(token);

  const modelsUnauthorized = await fetch(modelsUrl(status));
  assert.equal(modelsUnauthorized.status, 401);
  assert.equal((await modelsUnauthorized.json()).error.code, "unauthorized");

  const modelsAuthorized = await fetch(modelsUrl(status), {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  assert.equal(modelsAuthorized.status, 200);
  assert.deepEqual(await modelsAuthorized.json(), { models: [] });

  const modelsWrongMethodAfterAuth = await fetch(modelsUrl(status), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  assert.equal(modelsWrongMethodAfterAuth.status, 405);
  assert.equal((await modelsWrongMethodAfterAuth.json()).error.code, "method_not_allowed");

  const chatUnauthorized = await fetch(chatUrl(status), { method: "POST" });
  assert.equal(chatUnauthorized.status, 401);

  const chatAuthorized = await fetch(chatUrl(status), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  assert.equal(chatAuthorized.status, 415);
  assert.equal((await chatAuthorized.json()).error.code, "unsupported_media_type");

  const chatWrongMethodAfterAuth = await fetch(chatUrl(status), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  assert.equal(chatWrongMethodAfterAuth.status, 405);

  const streamUnauthorized = await fetch(streamUrl(status), { method: "POST" });
  assert.equal(streamUnauthorized.status, 401);

  const streamAuthorized = await fetch(streamUrl(status), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  assert.equal(streamAuthorized.status, 415);
  assert.equal((await streamAuthorized.json()).error.code, "unsupported_media_type");

  const streamWrongMethodAfterAuth = await fetch(streamUrl(status), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  assert.equal(streamWrongMethodAfterAuth.status, 405);

  await gateway.stop("command");
});

test("mapLanguageModelErrorCode maps NotFound to model_not_found", () => {
  const mapped = mapLanguageModelErrorCode({ code: "NotFound", message: "raw upstream detail" });
  assert.equal(mapped, "model_not_found");
});

test("mapLanguageModelErrorCode maps cancellation-like failures to cancelled", () => {
  assert.equal(mapLanguageModelErrorCode({ code: "CancelledByClient" }), "cancelled");
  assert.equal(mapLanguageModelErrorCode({ name: "CancellationError" }), "cancelled");
  assert.equal(mapLanguageModelErrorCode({ message: "request cancelled upstream" }), "cancelled");
});

test("token is accepted only via Authorization Bearer", async () => {
  const gateway = createGatewayController();
  await gateway.start();
  const status = gateway.getStatus();
  const token = gateway.getToken();
  assert.ok(token);

  const wrongScheme = await fetch(modelsUrl(status), {
    headers: {
      Authorization: `Token ${token}`,
    },
  });
  assert.equal(wrongScheme.status, 401);

  const wrongToken = await fetch(modelsUrl(status), {
    headers: {
      Authorization: "Bearer wrong-token",
    },
  });
  assert.equal(wrongToken.status, 401);

  const queryToken = await fetch(`${modelsUrl(status)}?token=${encodeURIComponent(token)}`);
  assert.equal(queryToken.status, 401);

  const altHeaderGateway = await fetch(modelsUrl(status), {
    headers: {
      "x-gateway-token": token,
    },
  });
  assert.equal(altHeaderGateway.status, 401);

  const altHeaderApiKey = await fetch(modelsUrl(status), {
    headers: {
      "x-api-key": token,
    },
  });
  assert.equal(altHeaderApiKey.status, 401);

  const cookieToken = await fetch(modelsUrl(status), {
    headers: {
      Cookie: `gateway_token=${token}`,
    },
  });
  assert.equal(cookieToken.status, 401);

  const validBearer = await fetch(modelsUrl(status), {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  assert.equal(validBearer.status, 200);
  assert.deepEqual(await validBearer.json(), { models: [] });

  await gateway.stop("command");
});

test("models listing calls model service only for authenticated GET", async () => {
  let listModelsCalls = 0;

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        listModelsCalls += 1;
        return [];
      },
    },
  });

  await gateway.start();
  const status = gateway.getStatus();
  const token = gateway.getToken();
  assert.ok(token);

  assert.equal(listModelsCalls, 0);

  const unauthorized = await fetch(modelsUrl(status));
  assert.equal(unauthorized.status, 401);
  assert.equal((await unauthorized.json()).error.code, "unauthorized");
  assert.equal(listModelsCalls, 0);

  const wrongMethodAfterAuth = await fetch(modelsUrl(status), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  assert.equal(wrongMethodAfterAuth.status, 405);
  assert.equal((await wrongMethodAfterAuth.json()).error.code, "method_not_allowed");
  assert.equal(listModelsCalls, 0);

  const authorized = await fetchAuthorizedModels(gateway);
  assert.equal(authorized.status, 200);
  assert.deepEqual(await authorized.json(), { models: [] });
  assert.equal(listModelsCalls, 1);

  await gateway.stop("command");
});

test("models listing maps VS Code model metadata and keeps IDs opaque", async () => {
  let selectChatModelsCalls = 0;
  let sendRequestCalls = 0;

  const fakeModelService = createVsCodeModelService({
    async selectChatModels(selector) {
      selectChatModelsCalls += 1;
      assert.deepEqual(selector, {});

      return [
        {
          id: "vendor/model:stable@2026.05",
          name: "Primary Model",
          vendor: "VendorA",
          family: "FamilyA",
          version: "2026.05",
          sendRequest() {
            sendRequestCalls += 1;
            throw new Error("sendRequest should not be called during model listing.");
          },
        },
        {
          id: "Opaque Id With Spaces / Do-Not-Normalize",
          name: "  ",
          vendor: "",
          family: "\t",
          version: "",
          sendRequest() {
            sendRequestCalls += 1;
            throw new Error("sendRequest should not be called during model listing.");
          },
        },
      ];
    },
  });

  const gateway = createGatewayController({ modelService: fakeModelService });

  assert.equal(selectChatModelsCalls, 0);
  await gateway.start();
  assert.equal(selectChatModelsCalls, 0);

  const response = await fetchAuthorizedModels(gateway);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), {
    models: [
      {
        id: "vendor/model:stable@2026.05",
        name: "Primary Model",
        vendor: "VendorA",
        family: "FamilyA",
        version: "2026.05",
        capabilities: {
          streaming: true,
          toolCalling: false,
          structuredOutput: false,
        },
      },
      {
        id: "Opaque Id With Spaces / Do-Not-Normalize",
        name: "Opaque Id With Spaces / Do-Not-Normalize",
        vendor: null,
        family: null,
        version: null,
        capabilities: {
          streaming: true,
          toolCalling: false,
          structuredOutput: false,
        },
      },
    ],
  });

  assert.equal(selectChatModelsCalls, 1);
  assert.equal(sendRequestCalls, 0);

  await gateway.stop("command");
});

test("models listing maps NoPermissions to sanitized access denied error", async () => {
  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        throw {
          code: "NoPermissions",
          message: "raw provider error should not leak",
        };
      },
    },
  });

  await gateway.start();

  const response = await fetchAuthorizedModels(gateway);
  assert.equal(response.status, 403);
  const body = await response.json();
  assert.equal(body.error.code, "model_access_denied");
  assert.equal(body.error.message, "Model access is denied.");
  assert.equal(body.error.message.includes("raw provider error"), false);

  await gateway.stop("command");
});

test("models listing maps Blocked to sanitized rate-limit error", async () => {
  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        throw {
          code: "Blocked",
          message: "provider quota details",
        };
      },
    },
  });

  await gateway.start();

  const response = await fetchAuthorizedModels(gateway);
  assert.equal(response.status, 429);
  const body = await response.json();
  assert.equal(body.error.code, "quota_or_rate_limited");
  assert.equal(body.error.message, "Model access is currently rate limited.");

  await gateway.stop("command");
});

test("models listing maps unknown failures to sanitized unknown_model_error", async () => {
  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        throw new Error("secret upstream stack details");
      },
    },
  });

  await gateway.start();

  const response = await fetchAuthorizedModels(gateway);
  assert.equal(response.status, 502);
  const body = await response.json();
  assert.equal(body.error.code, "unknown_model_error");
  assert.equal(body.error.message, "The model request failed.");
  assert.equal(body.error.message.includes("secret upstream"), false);

  await gateway.stop("command");
});

test("shutdown rejects request body", async () => {
  const gateway = createGatewayController();
  await gateway.start();
  const status = gateway.getStatus();
  const token = gateway.getToken();
  assert.ok(token);

  const withBody = await fetch(shutdownUrl(status), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ force: true }),
  });

  assert.equal(withBody.status, 400);
  const body = await withBody.json();
  assert.equal(body.error.code, "validation_error");

  await gateway.stop("command");
});

test("copy token helper fails gracefully when stopped and does not start gateway", async () => {
  const gateway = createGatewayController();
  assert.equal(gateway.getStatus().state, "stopped");

  const beforeCopy = gateway.getStatus().state;
  const copyResult = buildCopyTokenResult(gateway.getToken());
  const afterCopy = gateway.getStatus().state;

  assert.equal(beforeCopy, "stopped");
  assert.equal(copyResult.copied, false);
  assert.equal(copyResult.token, null);
  assert.match(copyResult.message, /not running/i);
  assert.equal(afterCopy, "stopped");
});

test("command message helpers never include token in status text", async () => {
  const gateway = createGatewayController();
  const started = await gateway.start();

  const statusMessage = buildStatusMessage(gateway.getStatus());
  assert.match(statusMessage.message, /running/i);
  const token = gateway.getToken();
  assert.ok(token);
  assert.equal(statusMessage.message.includes(token), false);

  const startMessage = buildStartMessage(started);
  assert.equal(startMessage.message.includes(token), false);

  const stopped = await gateway.stop("command");
  const stopMessage = buildStopMessage(stopped);
  assert.equal(stopMessage.message.includes(token), false);
});

test("deactivate path stop clears token on best effort", async () => {
  const gateway = createGatewayController();
  await gateway.start();
  assert.ok(gateway.getToken());

  const stopResult = await gateway.stop("deactivate");
  assert.equal(stopResult.outcome, "stopped");
  assert.equal(gateway.getStatus().state, "stopped");
  assert.equal(gateway.getToken(), null);
});