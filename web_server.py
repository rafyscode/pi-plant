import os
import sys
import json
import threading
import asyncio
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class CanvasHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        pass

class ReusableHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True

class WebCompanionServer:
    def __init__(self, event_queue, http_port=8080, ws_port=8765):
        self.event_queue = event_queue
        self.http_port = http_port
        self.ws_port = ws_port
        
        self.connected_clients = set()
        self.clients_lock = threading.Lock()
        
        self.httpd = None
        self.http_thread = None
        self.ws_thread = None
        self.ws_loop = None
        self._running = False

    def _start_http_server(self):
        """Starts the local HTTP server on port 8080."""
        try:
            self.httpd = ReusableHTTPServer(("0.0.0.0", self.http_port), CanvasHTTPHandler)
            print(f"WebCompanion: Living Canvas HTTP server running on port {self.http_port}")
            self.httpd.serve_forever()
        except Exception as e:
            print(f"WebCompanion HTTP server error: {e}")

    def _start_ws_server(self):
        """Starts the asynchronous WebSocket server on port 8765."""
        self.ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_loop)

        async def ws_handler(websocket):
            with self.clients_lock:
                self.connected_clients.add(websocket)
            print(f">>> [Phone Connected] Phone canvas attached ({websocket.remote_address})")

            # Send current idle state immediately on connect
            init_msg = json.dumps({"event": "STATE_CHANGE", "state": 0, "level": 0, "sentiment": "neutral"})
            try:
                await websocket.send(init_msg)
            except Exception:
                pass

            try:
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get("action") == "SWIPE":
                            tag = data.get("tag", "positive").lower()
                            readable = "Positive (+1)" if tag == "positive" else "Negative (-1)"
                            print(f">>> [Phone Stimulus] Swipe registered: {readable}")
                            self.event_queue.put({"type": "PHONE_SWIPE", "tag": tag})
                    except Exception as parse_err:
                        print(f"WebCompanion WS message error: {parse_err}")
            except Exception:
                pass
            finally:
                with self.clients_lock:
                    self.connected_clients.discard(websocket)
                print(">>> [Phone Disconnected] Phone canvas detached.")

        async def main_ws():
            import websockets
            # Start WebSocket server with reuse_address
            async with websockets.serve(ws_handler, "0.0.0.0", self.ws_port, reuse_address=True):
                print(f"WebCompanion: Real-time WebSocket server running on port {self.ws_port}")
                await asyncio.Future()

        try:
            self.ws_loop.run_until_complete(main_ws())
        except Exception as e:
            print(f"WebCompanion WS server error: {e}")

    def broadcast_state(self, state, level=0, sentiment="neutral"):
        """
        Broadcasts state change to all connected smartphones.
        Thread-safe: can be called synchronously from main.py.
        """
        payload = json.dumps({
            "event": "STATE_CHANGE",
            "state": state,
            "level": level,
            "sentiment": sentiment
        })

        if not self.ws_loop or not self.ws_loop.is_running():
            return

        async def _send_all():
            with self.clients_lock:
                clients = list(self.connected_clients)
            for ws in clients:
                try:
                    await ws.send(payload)
                except Exception:
                    pass

        asyncio.run_coroutine_threadsafe(_send_all(), self.ws_loop)

    def start(self):
        self._running = True
        self.http_thread = threading.Thread(target=self._start_http_server, daemon=True)
        self.http_thread.start()

        self.ws_thread = threading.Thread(target=self._start_ws_server, daemon=True)
        self.ws_thread.start()

    def stop(self):
        self._running = False
        if self.httpd:
            try:
                self.httpd.shutdown()
            except Exception:
                pass
        if self.ws_loop:
            try:
                self.ws_loop.stop()
            except Exception:
                pass
