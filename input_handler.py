import os
import sys
import threading
import time
import select

# Set up X11 environment if available
os.environ.setdefault("DISPLAY", ":0")
if "XAUTHORITY" not in os.environ and os.path.exists(os.path.expanduser("~/.Xauthority")):
    os.environ["XAUTHORITY"] = os.path.expanduser("~/.Xauthority")

class InputHandler:
    def __init__(self, event_queue):
        self.event_queue = event_queue
        self.pynput_listener = None
        self._running = False
        self._evdev_thread = None
        self._last_click_time = 0
        self._lock = threading.Lock()

    def _emit_click(self, tag):
        """Thread-safe event emitter with 250ms debouncing."""
        now = time.time()
        with self._lock:
            if now - self._last_click_time < 0.25:
                return
            self._last_click_time = now
            
        tag_clean = tag.lower()
        readable = "Positive (Watering / Right Click)" if tag_clean == "positive" else "Negative (Pain / Left Click)"
        print(f">>> [Physical Stimulus] Mouse Click registered: {readable}")
        self.event_queue.put({"type": "MOUSE_CLICKED", "tag": tag_clean})

    # --------------------------------------------------------------------------
    # Backend 1: evdev (Kernel-level /dev/input - Works 100% on Wayland & Headless)
    # --------------------------------------------------------------------------
    def _run_evdev_listener(self):
        try:
            import evdev
        except ImportError:
            print("InputHandler: evdev not installed.")
            return

        while self._running:
            # Continuously discover mouse devices in case of replug
            mouse_devices = []
            try:
                for path in evdev.list_devices():
                    try:
                        dev = evdev.InputDevice(path)
                        caps = dev.capabilities()
                        if evdev.ecodes.EV_KEY in caps:
                            keys = caps[evdev.ecodes.EV_KEY]
                            if evdev.ecodes.BTN_LEFT in keys or evdev.ecodes.BTN_RIGHT in keys:
                                mouse_devices.append(dev)
                    except (OSError, PermissionError):
                        continue
            except Exception as e:
                print(f"InputHandler: Error scanning input devices: {e}")

            if not mouse_devices:
                time.sleep(1.0)
                continue

            # Poll devices with select
            while self._running:
                try:
                    r, _, _ = select.select(mouse_devices, [], [], 0.5)
                    for dev in r:
                        try:
                            for event in dev.read():
                                if event.type == evdev.ecodes.EV_KEY and event.value == 1:  # Button Down
                                    if event.code == evdev.ecodes.BTN_RIGHT:
                                        self._emit_click("positive")
                                    elif event.code == evdev.ecodes.BTN_LEFT:
                                        self._emit_click("negative")
                        except (OSError, IOError):
                            # Device disconnected
                            break
                except Exception:
                    break
                
            time.sleep(0.5)

    # --------------------------------------------------------------------------
    # Backend 2: pynput (X11 / Desktop compatibility)
    # --------------------------------------------------------------------------
    def _on_pynput_click(self, x, y, button, pressed):
        if pressed:
            button_str = str(button).lower()
            if "right" in button_str:
                self._emit_click("positive")
            elif "left" in button_str:
                self._emit_click("negative")

    def start_listening(self):
        """Starts both kernel evdev and pynput listeners in background threads."""
        self._running = True
        
        # 1. Start evdev thread (Primary for Raspberry Pi Wayland / Headless)
        try:
            self._evdev_thread = threading.Thread(target=self._run_evdev_listener, daemon=True)
            self._evdev_thread.start()
            print("InputHandler: Kernel-level evdev mouse listener running.")
        except Exception as e:
            print(f"InputHandler: Failed to start evdev listener: {e}")

        # 2. Start pynput listener (Secondary for standard X11 environments)
        try:
            from pynput import mouse
            self.pynput_listener = mouse.Listener(on_click=self._on_pynput_click)
            self.pynput_listener.daemon = True
            self.pynput_listener.start()
            print("InputHandler: pynput mouse listener running.")
        except Exception as e:
            print(f"InputHandler: pynput listener not active ({e}).")

    def stop_listening(self):
        """Stops all active listeners."""
        self._running = False
        if self.pynput_listener:
            try:
                self.pynput_listener.stop()
            except Exception:
                pass
            self.pynput_listener = None
