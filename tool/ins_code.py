import hashlib
import hmac
import time


class KeyUtilities:
    def __init__(self):
        self.base32chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

    def dec2hex(self, s):
        return hex(int(s))[2:]

    def hex2dec(self, s):
        return int(s, 16)

    def base32tohex(self, base32):
        base32 = base32.replace(" ", "")  # 移除空格
        bits = ""
        hex_str = ""

        for char in base32:
            if char.upper() not in self.base32chars:
                raise ValueError(f"Invalid character '{char}' in Base32 string")
            val = self.base32chars.index(char.upper())
            bits += bin(val)[2:].zfill(5)

        for i in range(0, len(bits), 4):
            hex_str += self.dec2hex(int(bits[i:i + 4], 2))

        return hex_str

    def generate(self, secret, epoch=None):
        key = self.base32tohex(secret)
        if len(key) % 2 != 0:
            key += '0'

        if epoch is None:
            epoch = int(time.time())

        time_hex = self.dec2hex(int(epoch / 30)).zfill(16)

        key_bytes = bytes.fromhex(key)
        time_bytes = bytes.fromhex(time_hex)

        hmac_obj = hmac.new(key_bytes, time_bytes, hashlib.sha1)
        hmac_digest = hmac_obj.hexdigest()

        offset = int(hmac_digest[-1], 16)
        otp = (int(hmac_digest[offset * 2: offset * 2 + 8], 16) & 0x7fffffff) % 1000000
        return str(otp).zfill(6)


def get_deOne_code():
    return KeyUtilities().generate("JGO3 DSJQ BBCO RQGH C2LB AY6Q QBTS 4KOR")


if __name__ == '__main__':
    print(KeyUtilities().generate("JGO3 DSJQ BBCO RQGH C2LB AY6Q QBTS 4KOR"))
