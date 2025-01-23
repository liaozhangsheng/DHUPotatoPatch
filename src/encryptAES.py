from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64

_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
_chars_len = len(_chars)

def _gas(data, key0, iv0):
    key0 = key0.strip()
    key = key0.encode('utf-8')
    iv = iv0.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(encrypted).decode('utf-8')

def _rds(length):
    return ''.join(_chars[ord(get_random_bytes(1)) % _chars_len] for _ in range(length))

def encryptAES(data, _p1):
    if not _p1:
        return data
    encrypted = _gas(_rds(64) + data, _p1, _rds(16))
    return encrypted