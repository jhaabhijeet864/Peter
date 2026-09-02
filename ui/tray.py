import pystray
from PIL import Image, ImageDraw
import threading

class SystemTrayUI:
    """
    Enhanced System Tray UI with dynamic state indicators (colors) and threading.
    """
    def __init__(self, on_wake_cb, on_settings_cb, on_quit_cb):
        self.on_wake_cb = on_wake_cb
        self.on_settings_cb = on_settings_cb
        self.on_quit_cb = on_quit_cb
        self.icon = None
        self.state = "idle"

    def _create_image(self, color):
        """Generates an icon with a specific color."""
        image = Image.new('RGB', (64, 64), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((16, 16, 48, 48), fill=color)
        return image

    def set_state(self, new_state: str):
        """Changes the tray icon color based on Peter's state."""
        self.state = new_state
        if self.icon:
            if self.state == "listening":
                self.icon.icon = self._create_image((0, 255, 0)) # Green
            elif self.state == "speaking":
                self.icon.icon = self._create_image((0, 0, 255)) # Blue
            else:
                self.icon.icon = self._create_image((255, 255, 255)) # White

    def _on_wake(self, icon, item):
        self.set_state("listening")
        # Execute wake logic in a background thread to prevent UI freezing
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
            pystray.MenuItem("Settings", self._on_settings),
            pystray.MenuItem("Status: Online", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit)
        )
        # Default state is idle (White)
        self.icon = pystray.Icon("Peter", self._create_image((255, 255, 255)), "Peter AI Butler", menu)
        self.icon.run()
