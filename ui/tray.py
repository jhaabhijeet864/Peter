import pystray
from PIL import Image, ImageDraw
import threading

class SystemTrayUI:
    def __init__(self, on_wake_cb, on_settings_cb, on_quit_cb, 
                 get_models_cb, set_model_cb, current_model_cb,
                 get_plugins_cb, toggle_plugin_cb,
                 clear_context_cb, toggle_sleep_cb):
        
        # Base Callbacks
        self.on_wake_cb = on_wake_cb
        self.on_settings_cb = on_settings_cb
        self.on_quit_cb = on_quit_cb
        
        # Dynamic Model Callbacks
        self.get_models_cb = get_models_cb
        self.set_model_cb = set_model_cb
        self.current_model_cb = current_model_cb
        
        # Advanced Plugin & Quick Action Callbacks
        self.get_plugins_cb = get_plugins_cb
        self.toggle_plugin_cb = toggle_plugin_cb
        self.clear_context_cb = clear_context_cb
        self.toggle_sleep_cb = toggle_sleep_cb
        
        self.icon = None
        self.state = "idle"
        self.sleep_mode = False

    def _create_image(self, color):
        image = Image.new('RGB', (64, 64), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((16, 16, 48, 48), fill=color)
        return image

    def set_state(self, new_state: str):
        self.state = new_state
        if self.icon and not self.sleep_mode:
            if self.state == "listening":
                self.icon.icon = self._create_image((0, 255, 0)) # Green
            elif self.state == "speaking":
                self.icon.icon = self._create_image((0, 0, 255)) # Blue
            else:
                self.icon.icon = self._create_image((255, 255, 255)) # White

    def _generate_model_menu(self):
        try:
            models = self.get_models_cb()
            if not models:
                return [pystray.MenuItem("No models found", lambda: None, enabled=False)]
            
            items = []
            current = self.current_model_cb()
            for m in models:
                def create_cb(model_name):
                    return lambda icon, item: self.set_model_cb(model_name)
                    
                items.append(
                    pystray.MenuItem(
                        m, 
                        create_cb(m), 
                        checked=lambda item, model_name=m: current == model_name,
                        radio=True
                    )
                )
            return items
        except Exception:
            return [pystray.MenuItem("Ollama not running", lambda: None, enabled=False)]

    def _generate_plugin_menu(self):
        """Dynamically generates the submenu for enabling/disabling MCP tools."""
        try:
            plugins = self.get_plugins_cb()
            if not plugins:
                return [pystray.MenuItem("No plugins loaded", lambda: None, enabled=False)]
            
            items = []
            for p_name, p_enabled in plugins.items():
                def create_cb(name):
                    return lambda icon, item: self.toggle_plugin_cb(name)
                    
                items.append(
                    pystray.MenuItem(
                        p_name,
                        create_cb(p_name),
                        checked=lambda item, name=p_name: self.get_plugins_cb().get(name, False)
                    )
                )
            return items
        except Exception:
            return [pystray.MenuItem("Error loading plugins", lambda: None, enabled=False)]

    def _on_clear_context(self, icon, item):
        self.clear_context_cb()

    def _on_toggle_sleep(self, icon, item):
        self.sleep_mode = not self.sleep_mode
        self.toggle_sleep_cb(self.sleep_mode)
        if self.sleep_mode:
            self.icon.icon = self._create_image((128, 128, 128)) # Grey for sleep
        else:
            self.set_state("idle")

    def _on_wake(self, icon, item):
        if self.sleep_mode:
            return # Ignore manual wakes if sleeping
        self.set_state("listening")
        threading.Thread(target=self._run_wake, daemon=True).start()

    def _run_wake(self):
        self.on_wake_cb()
        self.set_state("idle")

    def _on_settings(self, icon, item):
        threading.Thread(target=self.on_settings_cb, daemon=True).start()

    def _on_quit(self, icon, item):
        self.on_quit_cb()
        if self.icon:
            self.icon.stop()

    def run(self):
        menu = pystray.Menu(
            pystray.MenuItem("Wake Peter", self._on_wake),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Model Selector", pystray.Menu(self._generate_model_menu)),
            pystray.MenuItem("MCP Plugins", pystray.Menu(self._generate_plugin_menu)),
            pystray.MenuItem("Quick Actions", pystray.Menu(
                pystray.MenuItem("Clear Context Memory", self._on_clear_context),
                pystray.MenuItem("Sleep Mode (Mute Mic)", self._on_toggle_sleep, checked=lambda item: self.sleep_mode)
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", self._on_settings),
            pystray.MenuItem("Status: Online", lambda: None, enabled=False),
            pystray.MenuItem("Quit", self._on_quit)
        )
        self.icon = pystray.Icon("Peter", self._create_image((255, 255, 255)), "Peter AI Butler", menu)
        self.icon.run()
