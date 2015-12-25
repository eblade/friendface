# -*- coding: utf-8 -*-

from enum import IntEnum
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA


class Privacy(IntEnum):
    deny = 0  # don't verify regardless who asks
    friends = 1  # verify only friends
    everyone = 2  # verify for everyone


class Verification(IntEnum):
    unverified = 0  # no verification is done
    verified = 1  # local verification ok
    source = 2  # remote challange-response verification ok
    invalid = 3  # verification failed


def generate_key_pair():
    """
    Generate a key pair.

    Returns (unicode private_key, unicode public_key)
    """
    private_key = RSA.generate(1024)
    public_key = private_key.publickey()
    return private_key.exportKey(), public_key.exportKey()


def verify(message):
    """
    Verify a signed message.

    Returns Message (with .verified set to verified or invalid)
    """
    message = message.copy()
    key = RSA.importKey(message.public_key)
    h = SHA.new(message.data)
    verifier = PKCS1_v1_5.new(key)
    message.verified = Verification.verified if verifier.verify(h, message.signature)\
        else Verification.invalid
    return message


def sign(message):
    """
    Generate new keys and sign a message.

    Returns Message (signed)
    """
    message = message.copy()
    message.private_key, message.public_key = generate_key_pair()
    key = RSA.importKey(message.private_key)
    h = SHA.new(message.data)
    signer = PKCS1_v1_5.new(key)
    message.signature = signer.sign(h)
    return message
