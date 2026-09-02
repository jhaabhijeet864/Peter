from .plugin_manager import PluginManager

class MCPServer:
    """
    Scalable MCP Server that loads tools dynamically using the PluginManager.
    """
    def __init__(self, server_name: str, plugins_package: str = "mcp.plugins"):
        self.server_name = server_name
        self.plugin_manager = PluginManager(plugins_package)
        self.plugin_manager.discover_and_load()
        self.tools = self.plugin_manager.get_tools()

    def execute(self, tool_name: str, **kwargs):
        if tool_name in self.tools:
            return self.tools[tool_name](**kwargs)
        raise ValueError(f"Tool '{tool_name}' not found in registered plugins.")
