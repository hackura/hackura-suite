import socket
import threading
import time
from core.db import db_manager

class C2Server:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.clients = {}
        self.server_socket = None
        self.running = False

    def start_server(self, callback=None):
        self.running = True
        self.server_thread = threading.Thread(target=self._listen, args=(callback,))
        self.server_thread.start()

    def _listen(self, callback):
        if callback: callback(f"[*] C2 Server listening on {self.host}:{self.port}...")
        # Simulation for environment safety
        while self.running:
            time.sleep(5)
            # Simulated check-in
            if not self.clients:
                client_id = "AGENT-X86-GH-5521"
                self.clients[client_id] = {"ip": "154.160.22.11", "os": "Windows 10", "status": "Active"}
                if callback: callback(f"[+] New connection received from {client_id} (Accra, GH)")
                db_manager.log_action("C2 Connection", f"Received from {client_id}")

    def stop_server(self):
        self.running = False

c2_server = C2Server()
