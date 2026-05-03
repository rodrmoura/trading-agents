from __future__ import annotations

import importlib
import sys
from collections.abc import Iterable

import pytest

pytest.importorskip("langchain_core")

import llm_gateway
from langchain_core.messages import (
    AIMessage,
    ChatMessage as LangChainChatMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from llm_gateway import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    GatewayClient,
    GatewayClientConfig,
    GatewayConfigurationError,
    GatewayErrorPayload,
    GatewayRequestError,
    GatewayToolCall,
    StreamChunkEvent,
    StreamDoneEvent,
    StreamErrorEvent,
)


class FakeGatewayClient(GatewayClient):
    def __init__(
        self,
        *,
        responses: Iterable[str | ChatResponse] = ("Gateway response",),
        stream_events: Iterable[object] = (),
        token: str = "synthetic-token",
    ) -> None:
        super().__init__(GatewayClientConfig(base_url="http://127.0.0.1:49152", token=token))
        self.requests: list[ChatRequest] = []
        self._responses = list(responses)
        self._stream_events = list(stream_events)

    def chat(self, request: ChatRequest) -> ChatResponse:
        self.requests.append(request)
        next_response = self._responses.pop(0) if self._responses else "Gateway response"
        if isinstance(next_response, ChatResponse):
            return next_response
        return ChatResponse(
            id="gwchat_test",
            model=request.model,
            created="2026-05-01T00:00:00.000Z",
            message=ChatMessage(role="assistant", content=next_response),
            finish_reason="stop",
        )

    def stream_chat(self, request: ChatRequest) -> Iterable[object]:
        self.requests.append(request)
        return iter(self._stream_events)


def make_model(client: FakeGatewayClient | None = None):
    from llm_gateway.langchain_adapter import GatewayChatModel

    return GatewayChatModel(client=client or FakeGatewayClient(), model="model-id")


@tool
def get_stock_data(ticker: str) -> str:
    """Fetch stock data for a ticker."""
    return f"data for {ticker}"


def test_root_import_remains_lightweight_without_adapter_module() -> None:
    module_name = "llm_gateway.langchain_adapter"
    sys.modules.pop(module_name, None)
    importlib.reload(llm_gateway)

    assert llm_gateway.__version__ == "0.0.1"
    assert module_name not in sys.modules


def test_adapter_module_imports_when_langchain_core_is_installed() -> None:
    module = importlib.import_module("llm_gateway.langchain_adapter")

    assert module.GatewayChatModel.__name__ == "GatewayChatModel"


def test_adapter_instantiates_with_stable_type_and_safe_repr() -> None:
    token = "synthetic-secret-token"
    adapter = make_model(FakeGatewayClient(token=token))

    assert adapter._llm_type == "llm_gateway"
    assert adapter._identifying_params == {"model": "model-id"}
    assert token not in repr(adapter)
    assert token not in str(adapter)
    assert token not in repr(adapter._identifying_params)


def test_invoke_text_returns_message_and_sends_native_user_message() -> None:
    client = FakeGatewayClient(responses=("Native answer",))
    adapter = make_model(client)

    message = adapter.invoke("Hello")

    assert isinstance(message, AIMessage)
    assert message.content == "Native answer"
    assert client.requests == [
        ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
    ]


def test_invoke_maps_langchain_message_roles_to_native_roles() -> None:
    client = FakeGatewayClient()
    adapter = make_model(client)

    adapter.invoke(
        [
            SystemMessage(content="System text"),
            HumanMessage(content="User text"),
            AIMessage(content="Assistant text"),
        ]
    )

    assert list(client.requests[0].messages) == [
        ChatMessage(role="system", content="System text"),
        ChatMessage(role="user", content="User text"),
        ChatMessage(role="assistant", content="Assistant text"),
    ]


def test_invoke_maps_list_of_dict_messages_to_native_roles() -> None:
    client = FakeGatewayClient()
    adapter = make_model(client)

    adapter.invoke(
        [
            {"role": "system", "content": "System text"},
            {"role": "user", "content": "User text"},
            {"role": "assistant", "content": "Assistant text"},
        ]
    )

    assert list(client.requests[0].messages) == [
        ChatMessage(role="system", content="System text"),
        ChatMessage(role="user", content="User text"),
        ChatMessage(role="assistant", content="Assistant text"),
    ]


def test_text_block_content_is_normalized_to_plain_text() -> None:
    client = FakeGatewayClient()
    adapter = make_model(client)

    adapter.invoke(
        [
            HumanMessage(
                content=[
                    "Alpha ",
                    {"type": "text", "text": "Beta"},
                    {"type": "image_url", "image_url": "ignored"},
                    {"type": "text", "text": " Gamma"},
                ]
            )
        ]
    )

    assert list(client.requests[0].messages) == [
        ChatMessage(role="user", content="Alpha Beta Gamma")
    ]


def test_unsupported_role_fails_without_prompt_leakage() -> None:
    adapter = make_model()
    prompt_text = "private prompt text"

    with pytest.raises(GatewayConfigurationError) as error_info:
        adapter.invoke([LangChainChatMessage(role="critic", content=prompt_text)])

    assert prompt_text not in str(error_info.value)


def test_unsupported_content_fails_without_prompt_leakage() -> None:
    adapter = make_model()
    prompt_text = "private text block"

    with pytest.raises(GatewayConfigurationError) as error_info:
        adapter.invoke([HumanMessage(content=[{"type": "text", "text": {"secret": prompt_text}}])])

    assert prompt_text not in str(error_info.value)


def test_chat_prompt_template_pipe_invokes_adapter() -> None:
    client = FakeGatewayClient(responses=("Pipe answer",))
    adapter = make_model(client)
    prompt = ChatPromptTemplate.from_messages(
        [("system", "Answer briefly."), ("human", "Say {word}")]
    )

    message = (prompt | adapter).invoke({"word": "hello"})

    assert message.content == "Pipe answer"
    assert list(client.requests[0].messages) == [
        ChatMessage(role="system", content="Answer briefly."),
        ChatMessage(role="user", content="Say hello"),
    ]


def test_stream_yields_native_text_chunks_and_allows_terminal_empty_chunk() -> None:
    client = FakeGatewayClient(
        stream_events=(
            StreamChunkEvent(text="Hel"),
            StreamChunkEvent(text="lo"),
            StreamDoneEvent(id="gwchat_stream", model="model-id", finish_reason="stop"),
        )
    )
    adapter = make_model(client)

    chunks = list(adapter.stream("Hello"))
    non_empty_content = [chunk.content for chunk in chunks if chunk.content]

    assert non_empty_content == ["Hel", "lo"]
    assert chunks[-1].content == ""
    assert list(client.requests[0].messages) == [ChatMessage(role="user", content="Hello")]


def test_stream_error_event_raises_request_error_without_token() -> None:
    token = "synthetic-stream-secret"
    client = FakeGatewayClient(
        stream_events=(
            StreamChunkEvent(text="partial"),
            StreamErrorEvent(
                error=GatewayErrorPayload(
                    code="stream_error",
                    message=f"Rejected bearer value {token}.",
                    request_id="gwreq_stream",
                )
            ),
        ),
        token=token,
    )
    adapter = make_model(client)

    with pytest.raises(GatewayRequestError) as error_info:
        list(adapter.stream("Hello"))

    assert token not in str(error_info.value)
    assert token not in repr(error_info.value)


def test_non_empty_stop_sequences_fail_without_prompt_leakage() -> None:
    adapter = make_model()
    prompt_text = "private stop prompt"

    with pytest.raises(NotImplementedError) as error_info:
        adapter.invoke(prompt_text, stop=["END"])

    assert prompt_text not in str(error_info.value)


def test_unsupported_generation_kwargs_fail_without_prompt_leakage() -> None:
    adapter = make_model()
    prompt_text = "private option prompt"

    with pytest.raises(ValueError) as error_info:
        adapter.invoke(prompt_text, temperature=0.2)

    assert "temperature" in str(error_info.value)
    assert prompt_text not in str(error_info.value)


def test_structured_output_deferred_and_fallback_to_free_text_invoke() -> None:
    client = FakeGatewayClient(responses=("Fallback answer",))
    adapter = make_model(client)

    try:
        adapter.with_structured_output({"type": "object"})
    except NotImplementedError:
        message = adapter.invoke("Use free text")

    assert message.content == "Fallback answer"


def test_bind_tools_with_real_tool_sends_native_tool_definitions() -> None:
    client = FakeGatewayClient(responses=("Tool-ready answer",))
    adapter = make_model(client).bind_tools([get_stock_data])

    message = adapter.invoke("Use a tool if needed.")

    assert message.content == "Tool-ready answer"
    assert len(client.requests) == 1
    assert len(client.requests[0].tools) == 1
    native_tool = client.requests[0].tools[0]
    assert native_tool.name == "get_stock_data"
    assert native_tool.description == "Fetch stock data for a ticker."
    assert native_tool.input_schema["type"] == "object"
    assert "ticker" in native_tool.input_schema["properties"]
    assert not hasattr(native_tool, "function")
    assert not hasattr(native_tool, "parameters")


def test_bind_tools_empty_returns_clone_that_omits_native_tools() -> None:
    client = FakeGatewayClient(responses=("No tools answer",))
    adapter = make_model(client)
    bound = adapter.bind_tools([])

    assert bound is not adapter
    bound.invoke("Hello")

    assert client.requests == [
        ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
    ]


def test_native_response_tool_calls_become_langchain_ai_message_tool_calls() -> None:
    response = ChatResponse(
        id="gwchat_tool",
        model="model-id",
        created="2026-05-01T00:00:00.000Z",
        message=ChatMessage(
            role="assistant",
            content="",
            tool_calls=(
                GatewayToolCall(id="call_1", name="get_stock_data", input={"ticker": "MSFT"}),
            ),
        ),
        finish_reason="toolCalls",
    )
    adapter = make_model(FakeGatewayClient(responses=(response,)))

    message = adapter.invoke("Fetch data.")

    assert isinstance(message, AIMessage)
    assert message.content == ""
    assert message.tool_calls == [
        {"name": "get_stock_data", "args": {"ticker": "MSFT"}, "id": "call_1", "type": "tool_call"}
    ]
    assert message.response_metadata["finish_reason"] == "toolCalls"


def test_prior_ai_tool_calls_and_tool_messages_serialize_to_native_messages() -> None:
    client = FakeGatewayClient()
    adapter = make_model(client).bind_tools([get_stock_data])

    adapter.invoke(
        [
            HumanMessage(content="Fetch MSFT."),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_stock_data",
                        "args": {"ticker": "MSFT"},
                        "id": "call_1",
                        "type": "tool_call",
                    }
                ],
            ),
            ToolMessage(content="price=123", tool_call_id="call_1"),
        ]
    )

    assert list(client.requests[0].messages) == [
        ChatMessage(role="user", content="Fetch MSFT."),
        ChatMessage(
            role="assistant",
            content="",
            tool_calls=(GatewayToolCall(id="call_1", name="get_stock_data", input={"ticker": "MSFT"}),),
        ),
        ChatMessage(role="tool", content="price=123", tool_call_id="call_1"),
    ]
    assert client.requests[0].tools[0].name == "get_stock_data"


def test_bind_tools_accepts_auto_tool_choice() -> None:
    client = FakeGatewayClient(responses=("Auto answer",))
    adapter = make_model(client).bind_tools([get_stock_data], tool_choice="auto")

    assert adapter.invoke("Hello").content == "Auto answer"
    assert client.requests[0].tools[0].name == "get_stock_data"


def test_bind_tools_rejects_unsupported_tool_choice_without_prompt_leakage() -> None:
    adapter = make_model()
    prompt_text = "private prompt text"

    with pytest.raises(NotImplementedError) as error_info:
        adapter.bind_tools([get_stock_data], tool_choice="required")

    assert prompt_text not in str(error_info.value)


def test_bind_tools_rejects_unsupported_kwargs_without_prompt_leakage() -> None:
    adapter = make_model()
    prompt_text = "private prompt text"

    with pytest.raises(ValueError) as error_info:
        adapter.bind_tools([get_stock_data], parallel_tool_calls=False)

    assert "parallel_tool_calls" in str(error_info.value)
    assert prompt_text not in str(error_info.value)