import os
import json
import requests

REMOTE_MARKETPLACE_URL = "https://api.hackura.io/v1/marketplace"

class PluginManager:
    def __init__(self):
        self.plugin_dir = os.path.join(os.path.expanduser("~"), "HackuraSuite", "plugins")
        os.makedirs(self.plugin_dir, exist_ok=True)
        self.manifest_path = os.path.join(self.plugin_dir, "manifest.json")
        self._ensure_manifest()

    def _ensure_manifest(self):
        if not os.path.exists(self.manifest_path):
            default_manifest = [
                {"id": "subfinder", "name": "Subdomain Elite Finder", "category": "OSINT", "rating": 5, "status": "Installed", "version": "1.0.0"},
                {"id": "nmap-pro", "name": "Nmap Advanced Scanner", "category": "Network", "rating": 5, "status": "Installed", "version": "7.94.0"},
                {"id": "secret-scan", "name": "Secrets Leak Hunter", "category": "Security", "rating": 5, "status": "Installed", "version": "2.4.1"},
                {"id": "s3-auditor", "name": "S3 Bucket Cloud Auditor", "category": "Cloud", "rating": 4, "status": "Installed", "version": "1.1.2"},
                {"id": "wpscan-wrapper", "name": "WPScan Pro Integration", "category": "Web", "rating": 5, "status": "Installed", "version": "3.8.22"},
                {"id": "hash-crack", "name": "Ultra Hash Cracker", "category": "Passwords", "rating": 5, "status": "Installed", "version": "6.2.6"},
                {"id": "sqlmap-pro", "name": "SQLMap Automation Pro", "category": "Injection", "rating": 5, "status": "Installed", "version": "1.7.5"},
                {"id": "c2-payload", "name": "C2 Persistence Generator", "category": "Post-Ex", "rating": 4, "status": "Installed", "version": "0.9.8"},
                {"id": "shodan-tool", "name": "Shodan Intelligence Query", "category": "Intelligence", "rating": 5, "status": "Installed", "version": "2.0.1"},
                {"id": "k8s-auditor", "name": "Docker/K8s Image Auditor", "category": "DevSecOps", "rating": 5, "status": "Installed", "version": "1.4.3"}
            ]
            with open(self.manifest_path, 'w') as f:
                json.dump(default_manifest, f, indent=4)

    def get_plugins(self):
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def sync_remote_plugins(self):
        """Fetch latest plugins from the remote marketplace and merge with local manifest."""
        try:
            resp = requests.get(REMOTE_MARKETPLACE_URL, timeout=10)
            if resp.status_code == 200:
                remote_plugins = resp.json()
                local_plugins = self.get_plugins()
                
                # Merge logic: preserved installed status
                installed_ids = {p['id'] for p in local_plugins if p['status'] == 'Installed'}
                
                final_list = []
                for p in remote_plugins:
                    if p['id'] in installed_ids:
                        p['status'] = 'Installed'
                    else:
                        p['status'] = 'Available'
                    final_list.append(p)
                
                with open(self.manifest_path, 'w') as f:
                    json.dump(final_list, f, indent=4)
                return True
        except Exception:
            return False
        return False

    def install_plugin(self, plugin_id):
        plugins = self.get_plugins()
        for p in plugins:
            if p['id'] == plugin_id:
                p['status'] = "Installed"
                break
        with open(self.manifest_path, 'w') as f:
            json.dump(plugins, f, indent=4)
        return True

plugin_manager = PluginManager()
