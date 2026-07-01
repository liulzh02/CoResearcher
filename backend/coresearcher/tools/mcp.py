from __future__ import annotations

from coresearcher.tools.registry import ToolDefinition, ToolSource


class McpToolCache:
    def __init__(self) -> None:
        self._server_tools: dict[str, list[ToolDefinition]] = {}

    def set_server_tools(self, server: str, tools: list[ToolDefinition]) -> None:
        self._server_tools[server] = [
            tool.model_copy(update={"source": ToolSource.MCP, "mcp_server": server})
            for tool in tools
        ]

    def list_tools(self, allowed_servers: list[str] | None = None) -> list[ToolDefinition]:
        allowed = set(allowed_servers) if allowed_servers is not None else None
        tools: list[ToolDefinition] = []
        for server, server_tools in self._server_tools.items():
            if allowed is not None and server not in allowed:
                continue
            tools.extend(server_tools)
        return tools
