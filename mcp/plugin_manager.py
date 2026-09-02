import importlib
import pkgutil
import inspect
from pathlib import Path

class PluginManager:
    """
    Dynamically discovers and loads MCP tool plugins from a specified package.
    """
    def __init__(self, plugins_package: str):
        self.plugins_package = plugins_package
        self.tools = {}

    def discover_and_load(self):
        try:
            package = importlib.import_module(self.plugins_package)
        except ImportError:
            print(f"Warning: Plugin package '{self.plugins_package}' not found.")
            return

        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            full_module_name = f"{self.plugins_package}.{module_name}"
            mod = importlib.import_module(full_module_name)
            self._register_functions(mod)

    def _register_functions(self, module):
        if hasattr(module, 'register_tools'):
            # If the module explicitly defines a register_tools function
            tools_from_mod = module.register_tools()
            self.tools.update(tools_from_mod)
        else:
            # Otherwise, auto-discover public functions
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith('_'):
                    self.tools[name] = func

    def get_tools(self):
        return self.tools
