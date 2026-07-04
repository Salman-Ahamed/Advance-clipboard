import threading
import time
import pyperclip
from storage import add_item

class ClipboardMonitor:
    def __init__(self, on_new_item=None):
        self._running = False
        self._thread = None
        self._last_text = ""
        self.on_new_item = on_new_item

    def start(self):
        if self._running:
            return
        self._running = True
        try:
            self._last_text = pyperclip.paste()
        except Exception:
            self._last_text = ""
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def _poll(self):
        while self._running:
            try:
                text = pyperclip.paste()
                if text and text != self._last_text:
                    self._last_text = text
                    items = add_item(text)
                    if self.on_new_item:
                        self.on_new_item(items)
            except Exception:
                pass
            time.sleep(0.5)

    def is_running(self):
        return self._running
