import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from session import hash_pin, sign, verify_pin, verify_signature


def test_pin_roundtrip():
    salt, digest = hash_pin("4321")
    assert verify_pin("4321", salt, digest)
    assert not verify_pin("0000", salt, digest)


def test_signature():
    key = os.urandom(32)
    sig = sign("user=42", key)
    assert verify_signature("user=42", sig, key)
    assert not verify_signature("user=43", sig, key)
