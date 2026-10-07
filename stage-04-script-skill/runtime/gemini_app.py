"""Launch the original app while preserving Gemini tool-call metadata.

Run from the stage directory:
    uv run streamlit run runtime/gemini_app.py

The pinned ChatOpenAI client discards Gemini's extra_content on tool calls.
This adapter preserves it in message history and restores it on subsequent
Chat Completions requests. Original agent, tools and skills stay unchanged.
"""

from copy import deepcopy
from pathlib import Path
import runpy
import sys
from urllib.parse import urlparse

from langchain_openai import ChatOpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

EXTRAS_KEY = "gemini_tool_call_extras"


class GeminiChatOpenAI(ChatOpenAI):
    """Round-trip actual provider metadata without inventing signatures."""

    def _create_chat_result(self, response, generation_info=None):
        result = super()._create_chat_result(response, generation_info)
        raw = response if isinstance(response, dict) else response.model_dump()
        for generation, choice in zip(result.generations, raw["choices"]):
            extras = {
                call["id"]: deepcopy(call["extra_content"])
                for call in choice["message"].get("tool_calls") or []
                if call.get("id") and "extra_content" in call
            }
            if extras:
                generation.message.additional_kwargs[EXTRAS_KEY] = extras
        return result

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        messages = self._convert_input(input_).to_messages()
        for message, wire_message in zip(messages, payload.get("messages", [])):
            extras = message.additional_kwargs.get(EXTRAS_KEY, {})
            for call in wire_message.get("tool_calls", []):
                if call.get("id") in extras:
                    call["extra_content"] = deepcopy(extras[call["id"]])
        return payload


def build_compatible_model(settings):
    kwargs = {"model": settings.model_name, "api_key": settings.api_key}
    if settings.base_url:
        kwargs["base_url"] = settings.base_url
    if urlparse(settings.base_url or "").hostname == "generativelanguage.googleapis.com":
        # Collect complete responses so provider metadata is not lost in chunks.
        return GeminiChatOpenAI(**kwargs, disable_streaming=True, use_responses_api=False)
    return ChatOpenAI(**kwargs)


if __name__ == "__main__":
    import agent

    agent.build_model = build_compatible_model
    runpy.run_path(str(PROJECT_ROOT / "app.py"), run_name="__main__")
