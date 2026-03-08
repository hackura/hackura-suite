import base64
import random
import string

class Obfuscator:
    def xor_encrypt(self, data, key=None):
        if not key:
            key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        encoded = []
        for i in range(len(data)):
            key_c = key[i % len(key)]
            encoded_c = chr(ord(data[i]) ^ ord(key_c))
            encoded.append(encoded_c)
        
        return "".join(encoded), key

    def b64_obfuscate(self, data):
        return base64.b64encode(data.encode()).decode()

    def generate_python_stub(self, encrypted_data, key):
        """Generates a Python stub that decrypts and executes the payload in memory."""
        stub = f"""
import base64
def x(d, k):
    return "".join([chr(ord(d[i]) ^ ord(k[i % len(k)])) for i in range(len(d))])

key = "{key}"
data = {repr(encrypted_data)}
exec(x(data, key))
"""
        return stub

obfuscator = Obfuscator()
