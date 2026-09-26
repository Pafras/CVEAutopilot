import hashlib
import hmac
import os


def hash_pin(pin, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)
    return salt, digest


def verify_pin(pin, salt, digest):
    return hmac.compare_digest(hash_pin(pin, salt)[1], digest)


def sign(message, key):
    return hmac.new(key, message.encode(), hashlib.sha256).hexdigest()


def verify_signature(message, signature, key):
    return hmac.compare_digest(sign(message, key), signature)
