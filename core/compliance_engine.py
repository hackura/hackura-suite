import yaml
import requests
from bs4 import BeautifulSoup
from core.db import db_manager

class ComplianceEngine:
    def __init__(self, rule_file):
        with open(rule_file, 'r') as f:
            self.config = yaml.safe_load(f)
        self.rules = self.config.get('rules', [])
        
    def audit_target(self, url):
        url = url.strip()
        if not url.startswith('http'):
            url = f'https://{url}'
            
        results = {
            "name": self.config['name'],
            "score": 0,
            "max_score": sum(r['score'] for r in self.rules),
            "findings": []
        }
        
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            page_text = soup.get_text().lower()
            
            for rule in self.rules:
                passed = False
                detail = ""
                
                if rule['check_type'] == 'keyword':
                    matches = [k for k in rule['keywords'] if k.lower() in page_text]
                    if matches:
                        passed = True
                        detail = f"Found keywords: {', '.join(matches)}"
                    else:
                        detail = "No relevant keywords found in page content."
                        
                elif rule['check_type'] == 'http_check':
                    if url.startswith('https://'):
                        passed = True
                        detail = "Connection is secured via HTTPS."
                    else:
                        detail = "Site is using insecure HTTP protocol."
                
                elif rule['check_type'] == 'manual':
                    passed = False
                    detail = "Requires manual verification against official registry."
                
                if passed:
                    results['score'] += rule['score']
                    
                results['findings'].append({
                    "id": rule['id'],
                    "section": rule['section'],
                    "passed": passed,
                    "severity": rule['severity'],
                    "detail": detail
                })
                
        except Exception as e:
            results['error'] = str(e)
            
        return results

    def save_audit(self, project_id, results):
        # Simplified logging
        db_manager.log_action("Compliance Audit", f"Audit: {results['name']} | Score: {results['score']}")
        # In a real app, we'd store the full JSON result in the database
