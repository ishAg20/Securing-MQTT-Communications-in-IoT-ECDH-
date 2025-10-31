from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

class ECDHHandler:
    def __init__(self):
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_bytes = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
    def regenerate_keys(self):
        self.__init__()
    def get_pub(self):
        return self.public_bytes.decode()
    def derive_shared(self, peer_pub_bytes):
        peer_pub = serialization.load_pem_public_key(peer_pub_bytes.encode())
        shared = self.private_key.exchange(ec.ECDH(), peer_pub)
        # Use HKDF to derive AES key from ECDH shared secret
        aes_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'handshake')
        return aes_key.derive(shared)
