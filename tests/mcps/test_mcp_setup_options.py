from pieces.command_registry import CommandRegistry
from pieces.mcp.integrations import claude_cli_integration, zed_integration
from pieces.pieces_argparser import PiecesArgparser


def test_zed_and_claude_code_support_workspace_options():
    assert zed_integration.options, "Zed should expose setup location options"
    assert claude_cli_integration.options, "Claude Code should expose setup location options"
    option_keys = {
        option_config["option"]
        for _, option_config in zed_integration.options + claude_cli_integration.options
    }
    assert {"global", "local"}.issubset(option_keys)


def test_coding_agent_alias_invokes_mcp_subcommands():
    parser = PiecesArgparser(description="test")
    CommandRegistry(parser).setup_parser(parser, "test")

    mcp_args = parser.parse_args(["mcp", "list"])
    coding_agent_args = parser.parse_args(["coding-agent", "list"])

    assert mcp_args.func == coding_agent_args.func
