import base64
import os

# set this enviroment variable to encode passwords
KEY = os.environ['GEZI_FB_AUTH_KEY']

def encode(clear):
    enc = []
    for i in range(len(clear)):
        key_c = KEY[i % len(KEY)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()


def decode(enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = KEY[i % len(KEY)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

# use this function to encode and set your email + ps in conf.json
# print(encode("Aslfst0p76?kappa"))
# print(decode('"w5jDk8Kqw5rDjsOdw5PCo8KSwpTCmQ=="'))