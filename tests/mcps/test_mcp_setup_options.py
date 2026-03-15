from pieces.command_interface.mcp_command_group import MCPCommandGroup
from pieces.mcp.integrations import claude_cli_integration, zed_integration


def test_zed_and_claude_code_support_workspace_options():
    assert zed_integration.options, "Zed should expose setup location options"
    assert claude_cli_integration.options, "Claude Code should expose setup location options"
    option_keys = {
        option_config["option"]
        for _, option_config in zed_integration.options + claude_cli_integration.options
    }
    assert {"global", "local"}.issubset(option_keys)


def test_mcp_command_group_exposes_coding_agent_alias():
    assert "coding-agent" in MCPCommandGroup.instance.aliases
