import pystray
from PIL import Image, ImageDraw
import threading

class SystemTrayUI:
    def __init__(self, on_wake_cb, on_settings_cb, on_quit_cb, 
                 get_models_cb, set_model_cb, current_model_cb,
                 get_plugins_cb, toggle_plugin_cb,
                 clear_context_cb, toggle_sleep_cb, on_services_cb,
                 get_mics_cb, set_mic_cb, current_mic_cb,
                 get_speakers_cb, set_speaker_cb, current_speaker_cb):
        
        # Base Callbacks
        self.on_wake_cb = on_wake_cb
        self.on_settings_cb = on_settings_cb
        self.on_quit_cb = on_quit_cb
        self.on_services_cb = on_services_cb
        
        # Dynamic Model Callbacks
        self.get_models_cb = get_models_cb
        self.set_model_cb = set_model_cb
        self.current_model_cb = current_model_cb
        
        # Hardware Audio Device Callbacks
        self.get_mics_cb = get_mics_cb
        self.set_mic_cb = set_mic_cb
        self.current_mic_cb = current_mic_cb
        
        self.get_speakers_cb = get_speakers_cb
        self.set_speaker_cb = set_speaker_cb
        self.current_speaker_cb = current_speaker_cb
        
        # Advanced Plugin & Quick Action Callbacks
        self.get_plugins_cb = get_plugins_cb
        self.toggle_plugin_cb = toggle_plugin_cb
        self.clear_context_cb = clear_context_cb
        self.toggle_sleep_cb = toggle_sleep_cb
        
        self.icon = None
        self.state = "idle"
        self.sleep_mode = False
        
        self.base_icon = None
        try:
            import os
            icon_path = os.path.abspath("assets/icons/Peter.ico")
            if os.path.exists(icon_path):
                self.base_icon = Image.open(icon_path).convert("RGBA")
        except Exception as e:
            print(f"[UI] Failed to load custom icon: {e}")

    def _create_image(self, color):
        if self.base_icon is not None:
            img = self.base_icon.copy()
            if color is not None:
                draw = ImageDraw.Draw(img)
                w, h = img.size
                # Draw a status dot in the bottom right corner
                dot_size = int(w * 0.35)
                pad = int(w * 0.05)
                x0, y0 = w - dot_size - pad, h - dot_size - pad
                x1, y1 = w - pad, h - pad
                
                # Dark outline for visibility
                draw.ellipse((x0-2, y0-2, x1+2, y1+2), fill=(30, 30, 30, 255))
                draw.ellipse((x0, y0, x1, y1), fill=color)
            return img
        else:
            # Fallback to the old colored circle
            image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
            if color is not None:
                draw = ImageDraw.Draw(image)
                draw.ellipse((16, 16, 48, 48), fill=color)
            else:
                draw = ImageDraw.Draw(image)
                draw.ellipse((16, 16, 48, 48), fill=(176, 181, 185, 255)) # Silver Idle
            return image

    def set_state(self, new_state: str):
        self.state = new_state
        if self.icon and not self.sleep_mode:
            if self.state == "listening":
                self.icon.icon = self._create_image((32, 194, 14, 255)) 
            elif self.state == "processing":
                self.icon.icon = self._create_image((255, 204, 0, 255)) 
            elif self.state == "speaking":
                self.icon.icon = self._create_image((0, 153, 255, 255)) 
            else:
                self.icon.icon = self._create_image(None)

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

    def _generate_mic_menu(self):
        try:
            mics = self.get_mics_cb()
            if not mics:
                return [pystray.MenuItem("No microphones found", lambda: None, enabled=False)]
            
            items = []
            current = self.current_mic_cb()
            for mic in mics:
                idx = mic["index"]
                name = mic["name"]
                # Only show first 30 chars to avoid tray bloat
                display_name = name[:30] + "..." if len(name) > 30 else name
                
                def create_cb(mic_index):
                    return lambda icon, item: self.set_mic_cb(mic_index)
                    
                items.append(pystray.MenuItem(
                    display_name, 
                    create_cb(idx), 
                    checked=lambda item, i=idx: current == i,
                    radio=True
                ))
            return items
        except Exception:
            return [pystray.MenuItem("Error loading mics", lambda: None, enabled=False)]

    def _generate_speaker_menu(self):
        try:
            speakers = self.get_speakers_cb()
            if not speakers:
                return [pystray.MenuItem("No speakers found", lambda: None, enabled=False)]
            
            items = []
            current = self.current_speaker_cb()
            for spk in speakers:
                idx = spk["index"]
                name = spk["name"]
                display_name = name[:30] + "..." if len(name) > 30 else name
                
                def create_cb(speaker_index):
                    return lambda icon, item: self.set_speaker_cb(speaker_index)
                    
                items.append(pystray.MenuItem(
                    display_name, 
                    create_cb(idx), 
                    checked=lambda item, i=idx: current == i,
                    radio=True
                ))
            return items
        except Exception:
            return [pystray.MenuItem("Error loading speakers", lambda: None, enabled=False)]

    def _on_clear_context(self, icon, item):
        self.clear_context_cb()

    def _on_toggle_sleep(self, icon, item):
        self.sleep_mode = not self.sleep_mode
        self.toggle_sleep_cb(self.sleep_mode)
        if self.sleep_mode:
            # Deep Obsidian / Dark Iron for Sleep Mode
            self.icon.icon = self._create_image((26, 28, 29, 255)) 
        else:
            self.set_state("idle")

    def _on_wake(self, icon, item):
        if self.sleep_mode:
            return # Ignore manual wakes if sleeping
            
        if self.state == "idle":
            self.set_state("listening")
            threading.Thread(target=self.on_wake_cb, daemon=True).start()
        elif self.state == "listening":
            self.set_state("idle")
            # The background autonomous thread watches for this state change to exit!
        elif self.state == "speaking":
            self.set_state("idle")
            # The background TTS streaming loop watches for this state change to abort!

    def _on_settings(self, icon, item):
        threading.Thread(target=self.on_settings_cb, daemon=True).start()

    def _on_services(self, icon, item):
        self.on_services_cb()

    def _on_quit(self, icon, item):
        self.on_quit_cb()
        if self.icon:
            self.icon.stop()

    def run(self):
        menu = pystray.Menu(
            pystray.MenuItem("Push-To-Talk (Toggle)", self._on_wake, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Microphone Selector", pystray.Menu(self._generate_mic_menu)),
            pystray.MenuItem("Speaker Selector", pystray.Menu(self._generate_speaker_menu)),
            pystray.MenuItem("Model Selector", pystray.Menu(self._generate_model_menu)),
            pystray.MenuItem("MCP Plugins", pystray.Menu(self._generate_plugin_menu)),
            pystray.MenuItem("Quick Actions", pystray.Menu(
                pystray.MenuItem("Clear Context Memory", self._on_clear_context),
                pystray.MenuItem("Sleep Mode (Mute Mic)", self._on_toggle_sleep, checked=lambda item: self.sleep_mode)
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", self._on_settings),
            pystray.MenuItem("Services Monitor", self._on_services),
            pystray.MenuItem("Quit", self._on_quit)
        )
        self.icon = pystray.Icon("Peter", self._create_image(None), "Peter AI Butler", menu)
        # Ensure it boots in Silver Idle mode
        self.set_state("idle")
        self.icon.run()
