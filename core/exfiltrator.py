import time
import base64
import requests
from PySide6.QtCore import QObject, Signal

class Exfiltrator(QObject):
    """Simulates common data exfiltration techniques for EDR/NDR testing."""
    progress = Signal(str)
    finished = Signal()

    def __init__(self, technique, target, data):
        super().__init__()
        self.technique = technique
        self.target = target
        self.data = data # String or bytes
        self.logs = []

    def _log(self, msg):
        self.logs.append(msg)
        self.progress.emit(msg)

    def run(self):
        self._log(f"Initializing {self.technique} exfiltration...")
        if self.technique == "HTTPS POST":
            self._exfiltrate_https()
        elif self.technique == "DNS (Simulated)":
            self._exfiltrate_dns()
        elif self.technique == "ICMP (Simulated)":
            self._exfiltrate_icmp()
        self.finished.emit()

    def _exfiltrate_https(self):
        chunks = [self.data[i:i+50] for i in range(0, len(self.data), 50)]
        if not chunks:
            self._log("[!] No data payload provided. Sending keep-alive beacon.")
            self._log("TX [HTTPS-POST]: beacon_id=hk-99 (Status: 200)")
        for i, chunk in enumerate(chunks):
            self._log(f"Uploading chunk {i+1}/{len(chunks)}...")
            time.sleep(0.5)
        self._log("HTTPS Exfiltration Simulation Complete.")

    def _exfiltrate_dns(self):
        encoded = base64.b32encode(self.data.encode() if isinstance(self.data, str) else self.data).decode().replace("=", "").lower()
        chunks = [encoded[i:i+30] for i in range(0, len(encoded), 30)]
        if not chunks:
            self._log("[!] Empty payload. Sending DNS heartbeat.")
            self._log(f"TX [DNS-Q]: heartbeat.{self.target}")
        else:
            self._log(f"Data encoded into {len(chunks)} DNS queries.")
            for i, chunk in enumerate(chunks):
                fqdn = f"v1-{i}.{chunk}.{self.target}"
                self._log(f"TX [DNS-Q]: {fqdn} (Type: A)")
                time.sleep(0.4)
        self._log("DNS Tunneling Simulation Finished Successfully.")

    def _exfiltrate_icmp(self):
        self._log("Detecting raw socket permissions...")
        time.sleep(0.5)
        self._log("Using ICMP Payload Injection (Simulated).")
        data_bytes = self.data.encode() if isinstance(self.data, str) else self.data
        if not data_bytes:
            self._log("[!] Payload missing. Sending empty echo request.")
            self._log(f"TX [ICMP-ECHO]: {self.target} (Payload: NULL)")
        else:
            hex_data = data_bytes.hex()
            chunks = [hex_data[i:i+16] for i in range(0, len(hex_data), 16)]
            for i, chunk in enumerate(chunks):
                self._log(f"TX [ICMP-ECHO]: {self.target} | Payload: {chunk}...")
                time.sleep(0.3)
        self._log("ICMP Exfiltration Sequence Completed.")
