"""Directory discovery: schema, errors, sorting, non-recursion and resolved boundaries."""

import json
import sys
from pathlib import Path

import pytest

import paths
from agent import TOOLS, build_agent
from langchain_core.messages import AIMessage, HumanMessage
from tests.conftest import ScriptedChatModel
from tests.test_files import make_symlink
from tools import list_files
from tools.files import _list


@pytest.fixture
def folder(tmp_path):
    ws = tmp_path / "workspace"
    (ws / "data" / "nested").mkdir(parents=True)
    (ws / "data" / "z.md").write_text("Z", encoding="utf-8")
    (ws / "data" / "a.md").write_text("A", encoding="utf-8")
    (ws / "data" / "nested" / "hidden.md").write_text("H", encoding="utf-8")
    return ws


def test_sorted_direct_entries_only(folder):
    assert _list(folder, "data") == {"ok": True, "path": "data", "entries": [
        {"name": "a.md", "path": "data/a.md", "type": "file"},
        {"name": "nested", "path": "data/nested", "type": "directory"},
        {"name": "z.md", "path": "data/z.md", "type": "file"},
    ]}
    assert _list(folder, "data/nested")["entries"][0]["name"] == "hidden.md"
    (folder / "empty").mkdir()
    assert _list(folder, "empty")["entries"] == []
    assert _list(folder, ".")["path"] == "."
    assert _list(folder, "data/../data/") == _list(folder, "data")


@pytest.mark.parametrize("path,code", [
    ("data/a.md", "NOT_A_DIRECTORY"), ("missing", "FILE_NOT_FOUND"),
    ("../outside", "PATH_OUTSIDE_WORKSPACE"), ("data/../../outside", "PATH_OUTSIDE_WORKSPACE"),
    ("", "INVALID_PATH"), ("~", "PATH_OUTSIDE_WORKSPACE"),
])
def test_invalid_paths_fail_clearly(folder, path, code):
    result = _list(folder, path)
    assert result["ok"] is False
    assert result["error"]["code"] == code
    assert "entries" not in result


def test_absolute_path_rejected(folder):
    assert _list(folder, str(folder / "data"))["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"


def test_io_errors_are_structured(folder, monkeypatch):
    def denied(self):
        raise PermissionError("synthetic test")
    monkeypatch.setattr(Path, "iterdir", denied)
    assert _list(folder, "data")["error"]["code"] == "IO_ERROR"


def test_external_directory_symlink_and_entry_rejected(folder):
    outside = folder.parent / "outside"
    outside.mkdir()
    make_symlink(folder / "data" / "escape", outside, target_is_directory=True)
    assert _list(folder, "data/escape")["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"
    assert _list(folder, "data")["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"


def test_internal_symlink_keeps_workspace_relative_entry_path(folder):
    make_symlink(folder / "data" / "alias.md", folder / "data" / "a.md")
    entries = _list(folder, "data")["entries"]
    assert entries[1] == {"name": "alias.md", "path": "data/alias.md", "type": "file"}


@pytest.mark.skipif(sys.platform != "win32", reason="Windows junction regression")
def test_windows_directory_junction_escape_rejected(folder):
    import _winapi
    outside = folder.parent / "outside"
    outside.mkdir()
    _winapi.CreateJunction(str(outside), str(folder / "data" / "escape"))
    assert _list(folder, "data/escape")["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"
    assert _list(folder, "data")["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"


def test_registered_schema_and_result_reaches_next_model_request(lab_dirs):
    model = ScriptedChatModel(responses=[
        AIMessage(content="", tool_calls=[{"id": "discover", "name": "list_files", "args": {"path": "data/policies"}}]),
        AIMessage(content="Found policies."),
    ])
    events = []
    for mode, chunk in build_agent(model).stream({"messages": [HumanMessage(content="Find documents")]}, stream_mode=["updates", "custom"]):
        if mode == "custom" and chunk.get("observer"):
            events.append(chunk)
    requests = [e["data"] for e in events if e["event"] == "model_request"]
    schema = next(t for t in requests[0]["tools"] if t["name"] == "list_files")
    assert schema["parameters"]["required"] == ["path"]
    tool_message = next(m for m in requests[1]["messages"] if m["role"] == "tool")
    assert tool_message["tool_call_id"] == "discover"
    result = json.loads(tool_message["content"])
    assert result["ok"] is True and len(result["entries"]) == 2
    assert json.loads(list_files.invoke({"path": "data/policies"})) == result
    assert [t.name for t in TOOLS] == ["read_file", "write_file", "list_files"]
