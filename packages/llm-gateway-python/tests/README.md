# Tests

Tests for the Python SDK live here and run with package-local pytest commands.

Current P3.4 coverage:

- local importability and package metadata
- no app-owned or command-line imports in package source
- token redaction in client configuration representations
- blocking native HTTP behavior for health, model listing, chat, and streaming chat
- native error envelope mapping
- native SSE parser behavior for chunk, done, and error events
- stream response cleanup on terminal events, parser errors, transport errors, and explicit iterator close
- shallow native gateway type construction
- optional LangChain Core adapter import, invocation, prompt-template composition, streaming, non-streaming native tool calls, parser-level structured output, fallback boundaries, and token-safe representations

Future packets own any gateway-native structured-output contract beyond the current adapter-level tool-call parser compatibility.
