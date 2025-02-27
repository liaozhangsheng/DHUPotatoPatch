from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64

_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'

def _gas(data, key0, iv0):
    key = key0.strip().encode('utf-8')
    iv = iv0.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(encrypted).decode('utf-8')

def _rds(length):
    return ''.join(_chars[ord(get_random_bytes(1)) % len(_chars)] for _ in range(length))

def encryptAES(data, _p1):
    if not _p1:
        return data
    encrypted = _gas(_rds(64) + data, _p1, _rds(16))
    return encrypted
