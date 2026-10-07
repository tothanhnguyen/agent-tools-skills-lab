"""LangChain agent của stage 04: Khởi tạo các công cụ và cấu hình Agent."""

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ToolCallLimitMiddleware
from langchain_openai import ChatOpenAI

import paths
from config import MODEL_CALL_LIMIT, TOOL_CALL_LIMIT, Settings
from observer import ObserverMiddleware
from prompts import build_system_prompt
from skill_catalog import Catalog, render_catalog, scan_skills
from tools import bash, read_file, write_file

TOOLS = [read_file, write_file, bash]


def build_model(settings: Settings) -> ChatOpenAI:
    model_params = {"model": settings.model_name, "api_key": settings.api_key}
    if settings.base_url:
        model_params["base_url"] = settings.base_url
    return ChatOpenAI(**model_params)


def load_catalog() -> Catalog:
    return scan_skills(paths.WORKSPACE_DIR)


def system_prompt() -> str:
    return build_system_prompt(render_catalog(load_catalog()))


def capabilities() -> dict:
    cat = load_catalog()
    return {"tools": [t.name for t in TOOLS], "skills": cat.metadata(), "skill_diagnostics": cat.diagnostics}


def build_agent(model):
    return create_agent(
        model=model,
        tools=TOOLS,
        system_prompt=system_prompt(),
        middleware=[
            ModelCallLimitMiddleware(run_limit=MODEL_CALL_LIMIT, exit_behavior="end"),
            ToolCallLimitMiddleware(run_limit=TOOL_CALL_LIMIT),
            ObserverMiddleware(),  # cuối danh sách = sát model/tool invocation nhất
        ],
    )
