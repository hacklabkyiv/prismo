import importlib

from flask import Flask


class PluginManager:
    def __init__(self, app: Flask):
        self.app = app
        self.plugins = {}

    def register_plugin(self, plugin_name: str):
        """Loads and registers a plugin by name."""
        try:
            plugin_module = importlib.import_module(f"plugins.{plugin_name}")
            if hasattr(plugin_module, "init_plugin"):
                plugin_module.init_plugin(self.app)  # Call plugin's initialization function
                self.plugins[plugin_name] = plugin_module
            else:
                raise RuntimeError(f"Plugin '{plugin_name}' does not have an "
                                   f"'init_plugin' function.")
        except ModuleNotFoundError as exc:
            raise RuntimeError(f"Plugin '{plugin_name}' not found.") from exc

    def load_plugins(self, plugin_names: list[str]):
        """Loads multiple plugins from a list of names."""
        # pylint: disable=broad-exception-caught
        for plugin_name in plugin_names:
            try:
                self.register_plugin(plugin_name)
                self.app.logger.info(f"Loaded plugin {plugin_name}")
            except Exception as e:
                self.app.logger.error(f"Error loading plugin {plugin_name}: {e}")
                continue
