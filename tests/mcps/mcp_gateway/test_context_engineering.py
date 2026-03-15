import os

from pieces.mcp.context_engineering import optimize_tool_arguments


class TestContextEngineering:
    def test_optimize_ask_pieces_ltm_adds_context_defaults(self, monkeypatch):
        monkeypatch.setenv("PIECES_CHAT_LLM", "gpt-4.1")
        monkeypatch.setenv("PIECES_CONNECTED_CLIENT", "zed")
        monkeypatch.setenv(
            "PIECES_OPEN_FILES", "src/main.py, ./tests/test_main.py , ,README.md"
        )

        optimized = optimize_tool_arguments(
            "ask_pieces_ltm",
            {"question": "What was I doing in Cursor and Chrome yesterday?"},
        )

        assert optimized["chat_llm"] == "gpt-4.1"
        assert optimized["connected_client"] == "zed"
        assert optimized["topics"]
        assert "Cursor" in optimized["application_sources"]
        assert "Google Chrome" in optimized["application_sources"]
        assert len(optimized["related_questions"]) == 2
        assert all(os.path.isabs(path) for path in optimized["open_files"])

    def test_optimize_create_memory_adds_project_and_summary_description(self):
        optimized = optimize_tool_arguments(
            "create_pieces_memory",
            {
                "summary": "Fixed a failing parser test. Added better MCP setup defaults.",
                "files": ["src/pieces/mcp/gateway.py", "README.md"],
            },
        )

        assert os.path.isabs(optimized["project"])
        assert optimized["summary_description"] == "Fixed a failing parser test"
        assert optimized["connected_client"] == "pieces-cli"
        assert all(os.path.isabs(path) for path in optimized["files"])
