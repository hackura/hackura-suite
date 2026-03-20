import socket
import threading
import time
from core.db import db_manager

class C2Server:
    def __init__(self, tcp_host='0.0.0.0', tcp_port=4444, http_host='127.0.0.2', http_port=4444):
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.http_host = http_host
        self.http_port = http_port
        self.clients = {}
        self.running = False

    def start_server(self, callback=None):
        self.running = True
        # TCP Agent Listener
        self.tcp_thread = threading.Thread(target=self._listen_tcp, args=(callback,), daemon=True)
        self.tcp_thread.start()
        # HTTP Dashboard Listener
        self.http_thread = threading.Thread(target=self._listen_http, daemon=True)
        self.http_thread.start()

    def _listen_tcp(self, callback):
        if callback: callback(f"[*] C2 TCP Listener active on {self.tcp_host}:{self.tcp_port}")
        
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.tcp_host, self.tcp_port))
            server.listen(5)
            server.settimeout(1.0)
            
            while self.running:
                try:
                    client, addr = server.accept()
                    client_id = f"AGENT-{addr[0]}-{int(time.time()) % 10000}"
                    self.clients[client_id] = {"ip": addr[0], "os": "Unknown (Checking...)", "status": "Active"}
                    if callback: callback(f"[+] Agent connected: {client_id} from {addr[0]}")
                    db_manager.log_action("C2 Connection", f"Received from {client_id}")
                    client.close() 
                except socket.timeout:
                    continue
        except Exception as e:
            if callback: callback(f"[!] TCP Listener Error: {e}")

    def _listen_http(self):
        """Serve a simple HTML dashboard on 127.0.0.2:4444"""
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.http_host, self.http_port))
            server.listen(5)
            server.settimeout(1.0)

            while self.running:
                try:
                    client, addr = server.accept()
                    data = client.recv(1024).decode()
                    
                    html = f"""
                    <html>
                    <head><style>
                        body {{ background: #121212; color: #ff3333; font-family: 'Courier New', monospace; padding: 20px; }}
                        h1 {{ border-bottom: 2px solid #ff3333; padding-bottom: 10px; }}
                        .agent {{ background: #1a1a1a; padding: 10px; margin: 10px 0; border: 1px solid #333; }}
                        .status {{ color: #00ff00; }}
                    </style></head>
                    <body>
                        <h1>HACKURA C2 ELITE DASHBOARD</h1>
                        <p>Server Time: {time.ctime()}</p>
                        <p>Listening on 0.0.0.0:4444 (TCP) / 127.0.0.2:4444 (HTTP)</p>
                        <hr>
                        <h3>Connected Intelligence Agents ({len(self.clients)})</h3>
                    """
                    for aid, info in self.clients.items():
                        html += f'<div class="agent">ID: {aid} | IP: {info["ip"]} | Status: <span class="status">{info["status"]}</span></div>'
                    
                    if not self.clients:
                        html += '<p>Waiting for beacon check-ins...</p>'
                        
                    html += "</body></html>"
                    
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
                    client.sendall(response.encode())
                    client.close()
                except socket.timeout:
                    continue
                except Exception:
                    continue
        except Exception:
            pass

    def stop_server(self):
        self.running = False

c2_server = C2Server()
