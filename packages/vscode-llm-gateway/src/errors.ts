import type { ServerResponse } from "node:http";

type NativeErrorCode =
  | "invalid_json"
  | "validation_error"
  | "unauthorized"
  | "model_access_denied"
  | "not_found"
  | "model_not_found"
  | "method_not_allowed"
  | "unsupported_media_type"
  | "quota_or_rate_limited"
  | "cancelled"
  | "not_implemented"
  | "unknown_model_error"
  | "internal_error"
  | "gateway_not_ready";

const STATUS_BY_CODE: Record<NativeErrorCode, number> = {
  invalid_json: 400,
  validation_error: 400,
  unauthorized: 401,
  model_access_denied: 403,
  not_found: 404,
  model_not_found: 404,
  method_not_allowed: 405,
  unsupported_media_type: 415,
  quota_or_rate_limited: 429,
  cancelled: 499,
  not_implemented: 501,
  unknown_model_error: 502,
  internal_error: 500,
  gateway_not_ready: 503,
};

const MESSAGE_BY_CODE: Record<NativeErrorCode, string> = {
  invalid_json: "Request JSON is invalid.",
  validation_error: "Request validation failed.",
  unauthorized: "Authorization failed.",
  model_access_denied: "Model access is denied.",
  not_found: "The requested endpoint was not found.",
  model_not_found: "The requested model was not found.",
  method_not_allowed: "HTTP method is not allowed for this endpoint.",
  unsupported_media_type: "Content-Type is not supported.",
  quota_or_rate_limited: "Model access is currently rate limited.",
  cancelled: "The request was cancelled.",
  not_implemented: "Endpoint is reserved but not implemented.",
  unknown_model_error: "The model request failed.",
  internal_error: "The gateway failed to process the request.",
  gateway_not_ready: "Gateway is not ready to process the request.",
};

export interface NativeErrorEnvelope {
  readonly error: {
    readonly code: NativeErrorCode;
    readonly message: string;
    readonly requestId: string;
    readonly metadata: Record<string, never>;
  };
}

export interface NativeErrorDetails {
  readonly statusCode: number;
  readonly body: NativeErrorEnvelope;
}

let requestCounter = 0;

function buildRequestId(): string {
  requestCounter += 1;
  return `gwreq_${String(requestCounter).padStart(8, "0")}`;
}

export function createNativeError(code: NativeErrorCode): NativeErrorDetails {
  return {
    statusCode: STATUS_BY_CODE[code],
    body: {
      error: {
        code,
        message: MESSAGE_BY_CODE[code],
        requestId: buildRequestId(),
        metadata: {},
      },
    },
  };
}

export function sendJson(response: ServerResponse, statusCode: number, payload: unknown): void {
  if (response.headersSent) {
    return;
  }

  response.statusCode = statusCode;
  response.setHeader("Content-Type", "application/json; charset=utf-8");
  response.end(JSON.stringify(payload));
}

export function sendNativeError(response: ServerResponse, code: NativeErrorCode): void {
  const details = createNativeError(code);
  sendJson(response, details.statusCode, details.body);
}

export type { NativeErrorCode };