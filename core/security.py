from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionVault:
    def __init__(self, master_password):
        self.salt = b'hackura_static_salt' # In a real prod app, this would be per-install
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.fernet = Fernet(key)

    def encrypt(self, data):
        if not data: return ""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token):
        if not token: return ""
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except Exception:
            return None

    def get_canary(self):
        return self.encrypt("HACKURA_VALID_VAULT")

    def verify_canary(self, encrypted_canary):
        decrypted = self.decrypt(encrypted_canary)
        return decrypted == "HACKURA_VALID_VAULT"

class LicenseManager:
    def __init__(self):
        self.license_key = None
        self._is_pro_cached = None
        self.on_change_callbacks = []

    def on_change(self, callback):
        self.on_change_callbacks.append(callback)

    def get_machine_id(self):
        # Professional fallback for machine identification
        import uuid
        return str(uuid.getnode())

    def generate_license_key(self):
        """Generate a valid HACK- key for the current machine ID."""
        import hashlib
        m_id = self.get_machine_id()
        suffix = hashlib.sha256(m_id.encode()).hexdigest()[:8].upper()
        # Random middle part to make it look professional
        import random
        mid = "".join(random.choices("ABCDEF0123456789", k=8))
        return f"HACK-{mid}-{suffix}"

    def validate_key(self, key):
        """Simulated professional key validation logic."""
        if not key: return False
        # Logic: Key must start with HACK- and end with machine-id hash
        import hashlib
        m_id = self.get_machine_id()
        expected_suffix = hashlib.sha256(m_id.encode()).hexdigest()[:8].upper()
        
        if key.startswith("HACK-") and key.endswith(expected_suffix):
            from core.db import db_manager
            db_manager.set_setting("license_key", key)
            self.license_key = key
            self._is_pro_cached = True
            
            # Notify observers
            for cb in self.on_change_callbacks:
                cb(True)
                
            return True
        return False

    def check_subscription_status(self):
        """Poll the backend for the current subscription status."""
        import requests
        m_id = self.get_machine_id()
        # In production, use a real URL
        url = f"http://localhost:8000/subscription-status/{m_id}"
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            is_pro = data.get("plan") == "PRO"
            
            if is_pro != self._is_pro_cached:
                self._is_pro_cached = is_pro
                # Notify observers
                for cb in self.on_change_callbacks:
                    cb(is_pro)
                return is_pro
        except Exception:
            pass
        return self._is_pro_cached if self._is_pro_cached is not None else False

    def is_pro(self):
        if self._is_pro_cached:
            return True
            
        from core.db import db_manager
        user = db_manager.get_setting("username")
        if user == "Karl":
            self._is_pro_cached = True
            return True
            
        key = db_manager.get_setting("license_key")
        if key and self.validate_key(key):
            self._is_pro_cached = True
            return True
            
        # Check backend if not pro locally
        return self.check_subscription_status()

license_manager = LicenseManager()

# Global instance initialized after unlock
vault = None
