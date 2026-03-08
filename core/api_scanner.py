import requests
import re
import json
from wrappers.ffuf_wrapper import FfufWrapper
from core.db import db_manager

class APIScanner:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.fuzzer = FfufWrapper()
        
    def discover_endpoints(self):
        """
        Attempts to discover API endpoints via common paths and documentation.
        """
        discovery_paths = [
            '/api', '/api/v1', '/api/v2', '/v1', '/v2', 
            '/swagger.json', '/openapi.json', '/graphql', 
            '/api/graphql', '/graphiql'
        ]
        
        found = []
        for path in discovery_paths:
            try:
                url = f"{self.base_url}{path}"
                resp = requests.get(url, timeout=5)
                if resp.status_code in [200, 401, 403]:
                    found.append(path)
            except:
                continue
        return found

    def parse_graphql_schema(self, endpoint):
        """
        Basic GraphQL introspection attempt.
        """
        query = {"query": "{ __schema { queryType { name } } }"}
        try:
            url = f"{self.base_url}{endpoint}"
            resp = requests.post(url, json=query, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if 'data' in data:
                    return True # Simplified for PoC
        except:
            pass
        return False

    def start_fuzzing(self, endpoint, wordlist_path, callback=None):
        """
        Starts ffuf on a specific endpoint.
        """
        full_url = f"{self.base_url}{endpoint}/FUZZ"
        if not self.fuzzer.is_available():
            if callback: callback("ERROR: ffuf not installed")
            return None
            
        process = self.fuzzer.fuzz(full_url, wordlist_path, ["-mc", "200,201,204,401,403"])
        return process

    def log_finding(self, scan_id, title, severity, description):
        db_manager.log_action("API Finding", f"{severity}: {title}")
        # Logic to insert into findings table
        conn = db_manager.get_connection()
        conn.execute(
            "INSERT INTO findings (scan_id, severity, title, description) VALUES (?, ?, ?, ?)",
            (scan_id, severity, title, description)
        )
        conn.commit()
