"""Provider metadata survives real LangChain response/request conversion."""

from copy import deepcopy

from langchain_core.messages import HumanMessage, ToolMessage

from config import Settings
from runtime.gemini_app import EXTRAS_KEY, GeminiChatOpenAI, build_compatible_model


def test_signatures_round_trip_by_call_id_and_do_not_mutate_response():
    model = GeminiChatOpenAI(model="gemini-test", api_key="not-a-real-key", disable_streaming=True)
    calls = [
        {"id": "read-1", "type": "function", "function": {"name": "read_file", "arguments": '{"path":"data/test.md"}'},
         "extra_content": {"google": {"thought_signature": "opaque-provider-value"}}},
        {"id": "read-2", "type": "function", "function": {"name": "read_file", "arguments": '{"path":"data/other.md"}'}},
    ]
    raw = {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": calls}, "finish_reason": "tool_calls"}]}
    original = deepcopy(raw)
    message = model._create_chat_result(raw).generations[0].message
    assert len(message.tool_calls) == 2
    payload = model._get_request_payload([
        HumanMessage(content="Read files"), message,
        ToolMessage(content="file contents", tool_call_id="read-1"),
        ToolMessage(content="other contents", tool_call_id="read-2"),
    ])
    wire_calls = payload["messages"][1]["tool_calls"]
    assert wire_calls[0]["extra_content"] == calls[0]["extra_content"]
    assert "extra_content" not in wire_calls[1]
    wire_calls[0]["extra_content"]["google"]["thought_signature"] = "changed"
    assert message.additional_kwargs[EXTRAS_KEY]["read-1"] == calls[0]["extra_content"]
    assert raw == original


def test_adapter_selected_only_for_google_endpoint():
    google = build_compatible_model(Settings("not-a-real-key", "gemini-test", "https://generativelanguage.googleapis.com/v1beta/openai/"))
    other = build_compatible_model(Settings("not-a-real-key", "other-model", "https://example.com/v1"))
    assert isinstance(google, GeminiChatOpenAI)
    assert google.disable_streaming is True
    assert google.use_responses_api is False
    assert type(other).__name__ == "ChatOpenAI"
