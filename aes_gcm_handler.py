from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64, json, time

class AESGCMHandler:
    def __init__(self, key):
        self.key = key
    def encrypt(self, data):
        b = json.dumps(data).encode() if not isinstance(data, bytes) else data
        cipher = AES.new(self.key, AES.MODE_GCM)
        ct, tag = cipher.encrypt_and_digest(b)
        return {
            'ciphertext': base64.b64encode(ct).decode(),
            'nonce': base64.b64encode(cipher.nonce).decode(),
            'tag': base64.b64encode(tag).decode(),
            'mode': 'GCM'
        }
    def decrypt(self, payload):
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=base64.b64decode(payload['nonce']))
        return json.loads(cipher.decrypt_and_verify(base64.b64decode(payload['ciphertext']), base64.b64decode(payload['tag'])))
