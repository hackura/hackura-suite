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

    def get_machine_id(self):
        # Professional fallback for machine identification
        import uuid
        return str(uuid.getnode())

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
            return True
        return False

    def is_pro(self):
        if self._is_pro_cached is not None:
            return self._is_pro_cached
            
        from core.db import db_manager
        key = db_manager.get_setting("license_key")
        if not key:
            self._is_pro_cached = False
            return False
            
        # Re-validate
        self._is_pro_cached = self.validate_key(key)
        return self._is_pro_cached

license_manager = LicenseManager()

# Global instance initialized after unlock
vault = None
