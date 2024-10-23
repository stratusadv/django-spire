import binascii
import os


def random_64_char_token():
    return str(binascii.hexlify(os.urandom(32)).decode())
