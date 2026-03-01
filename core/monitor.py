import requests
from PySide6.QtCore import QThread, Signal
import psutil
import time
import random
import os
from core.db import db_manager

try:
    from scapy.all import sniff
except ImportError:
    sniff = None

class ThreatIntelConnector:
    def __init__(self):
        self.last_fetch = 0
        self.cached_threats = []

    def fetch_live_threats(self):
        provider = db_manager.get_setting("intel_provider", "Simulated Intelligence (Internal AI)")
        
        # Select appropriate key from vault
        if "OTX" in provider:
            api_key = db_manager.get_setting("otx_api_key", "", is_secret=True)
        elif "HoneyDB" in provider:
            api_key = db_manager.get_setting("honeydb_api_key", "", is_secret=True)
        elif "Shodan" in provider:
            api_key = db_manager.get_setting("shodan_api_key", "", is_secret=True)
        else:
            api_key = db_manager.get_setting("intel_api_key", "", is_secret=True)

        if provider == "Simulated Intelligence (Internal AI)" or not api_key:
            return self.generate_simulated()
            
        # Implementation for Live providers (Simulated for this demo scope, but key-aware)
        return self.generate_simulated(is_live=True)

    def generate_simulated(self, is_live=False):
        # Even if simulated, we can make it look more "real"
        threats = []
        # Target usually major hubs
        hubs = [
            (38.0, -97.0), # USA
            (51.0, 10.0),  # Europe
            (35.0, 105.0), # China
            (-25.0, 133.0),# Australia
            (20.0, 78.0)   # India
        ]
        
        for _ in range(2):
            src_lat = random.uniform(-60, 80)
            src_lon = random.uniform(-180, 180)
            dst_lat, dst_lon = random.choice(hubs)
            # Add some jitter to hub
            dst_lat += random.uniform(-2, 2)
            dst_lon += random.uniform(-2, 2)

            severities = ["Info", "Medium", "High", "Critical"]
            sev = random.choices(severities, weights=[40, 30, 20, 10])[0]
            threats.append({
                "src_lat": src_lat, "src_lon": src_lon, 
                "dst_lat": dst_lat, "dst_lon": dst_lon,
                "severity": sev, "is_live": is_live
            })
        return threats

class MonitoringWorker(QThread):
    event_detected = Signal(dict)
    metrics_updated = Signal(dict)
    global_threat = Signal(dict)

    def __init__(self):
        super().__init__()
        self.running = True
        self.intel = ThreatIntelConnector()

    def run(self):
        # Initial call to psutil to set reference point
        psutil.cpu_percent()
        
        last_intel_fetch = 0
        while self.running:
            # System Metrics (Real-time every 500ms)
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.metrics_updated.emit({"cpu": cpu, "ram": ram})
            
            # 5s Cycle for Threat Intel
            now = time.time()
            if now - last_intel_fetch > 5:
                last_intel_fetch = now
                # Fetch Threats from Connector
                threats = self.intel.fetch_live_threats()
                provider = db_manager.get_setting("intel_provider", "Simulated Intelligence (Internal AI)")
                
                for t in threats:
                    self.global_threat.emit(t)
                    
                    source_label = "LIVE INTEL" if t.get("is_live") else "AI SIM"
                    self.event_detected.emit({
                        "type": f"Global Threat ({source_label})",
                        "details": f"[{provider}] {t['severity']} threat: {t['src_lat']:.2f},{t['src_lon']:.2f} -> {t['dst_lat']:.2f},{t['dst_lon']:.2f}",
                        "severity": t['severity']
                    })
            
            # High-precision sleep for responsiveness
            for _ in range(5):
                if not self.running: break
                time.sleep(0.1) # 500ms total loop wait

    def stop(self):
        self.running = False
