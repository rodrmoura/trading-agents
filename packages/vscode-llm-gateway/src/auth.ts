import type { IncomingMessage, ServerResponse } from "node:http";
import { timingSafeEqual } from "node:crypto";
import { sendNativeError } from "./errors";

export type TokenProvider = () => string | null;

function hasRejectedTokenTransport(request: IncomingMessage): boolean {
  const url = request.url ?? "";
  const questionIndex = url.indexOf("?");

  if (questionIndex >= 0) {
    const query = new URLSearchParams(url.slice(questionIndex + 1));
    if (query.has("token") || query.has("gateway_token") || query.has("access_token")) {
      return true;
    }
  }

  const cookieHeader = request.headers.cookie;
  if (typeof cookieHeader === "string" && cookieHeader.trim().length > 0) {
    return true;
  }

  if (request.headers["x-gateway-token"] !== undefined || request.headers["x-api-key"] !== undefined) {
    return true;
  }

  return false;
}

export function isAuthorized(request: IncomingMessage, tokenProvider: TokenProvider): boolean {
  if (hasRejectedTokenTransport(request)) {
    return false;
  }

  const expectedToken = tokenProvider();
  if (!expectedToken) {
    return false;
  }

  const authorizationHeader = request.headers.authorization;
  if (typeof authorizationHeader !== "string") {
    return false;
  }

  const match = /^Bearer\s+(.+)$/.exec(authorizationHeader);
  if (!match) {
    return false;
  }

  const incomingToken = match[1].trim();
  if (incomingToken.length === 0) {
    return false;
  }

  const incomingTokenBuffer = Buffer.from(incomingToken, "utf8");
  const expectedTokenBuffer = Buffer.from(expectedToken, "utf8");

  if (incomingTokenBuffer.length !== expectedTokenBuffer.length) {
    return false;
  }

  return timingSafeEqual(incomingTokenBuffer, expectedTokenBuffer);
}

export function ensureAuthorized(
  request: IncomingMessage,
  response: ServerResponse,
  tokenProvider: TokenProvider
): boolean {
  if (!isAuthorized(request, tokenProvider)) {
    sendNativeError(response, "unauthorized");
    return false;
  }

  return true;
}