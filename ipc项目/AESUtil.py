from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AESUtil:
    @staticmethod
    def encrypt(key: str, message: str) -> str:
        assert key is not None and len(key) in [16, 24, 32], "Key must be 16/24/32 bytes"
        assert message is not None, "Message cannot be null"

        key_bytes = key.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv=key_bytes)
        encrypted = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
        return AESUtil.to_hex_string(encrypted)

    @staticmethod
    def decrypt(key: str, hex_cipher: str) -> str:
        assert key is not None and len(key) in [16, 24, 32], "Key must be 16/24/32 bytes"
        assert hex_cipher is not None, "Cipher text cannot be null"

        key_bytes = key.encode('utf-8')
        cipher_bytes = AESUtil.convert_hex_string(hex_cipher)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv=key_bytes)
        decrypted = unpad(cipher.decrypt(cipher_bytes), AES.block_size)
        return decrypted.decode('utf-8')

    @staticmethod
    def convert_hex_string(hex_str: str) -> bytes:
        return bytes.fromhex(hex_str)

    @staticmethod
    def to_hex_string(byte_data: bytes) -> str:
        return ''.join(f'{b:02x}' for b in byte_data)
