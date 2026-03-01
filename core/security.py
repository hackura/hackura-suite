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

# Global instance initialized after unlock
vault = None
