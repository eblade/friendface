# -*- coding: utf-8 -*-

import os
import logging

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

    Returns (private_key, public_key)
    """
    private_key = RSA.generate(1024)
    public_key = private_key.publickey()
    return private_key, public_key


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
    private_key, public_key = generate_key_pair()
    message.private_key = private_key.exportKey()
    message.public_key = public_key.exportKey()
    h = SHA.new(message.data)
    signer = PKCS1_v1_5.new(private_key)
    message.signature = signer.sign(h)
    return message


def get_global_keys(private_key_path, public_key_path):
    """
    Read or create and store a global key pair given two paths.

    Returns (public key, private key)
    """
    private_key_path = os.path.expanduser(os.path.expandvars(private_key_path))
    public_key_path = os.path.expanduser(os.path.expandvars(public_key_path))

    write_private, write_public = False, False

    if os.path.exists(private_key_path):
        logging.info("Using private global key at %s." % private_key_path)
        with open(private_key_path) as f:
            private_key_str = f.read()
            private_key = RSA.importKey(private_key_str)
        if os.path.exists(public_key_path):
            logging.info("Using public global key at %s." % public_key_path)
            with open(public_key_path) as f:
                public_key_str = f.read()
            public_key = RSA.importKey(public_key_str)
        else:
            logging.info("Public global key from private key.")
            public_key = private_key.publickey()
            write_public = True

    else:
        private_key, public_key = generate_key_pair()
        write_private = True
        write_public = True
        logging.info("Generated new global keys.")

    if write_private:
        logging.info("Saving private global key to %s." % private_key_path)
        os.makedirs(os.path.dirname(private_key_path), exist_ok=True)
        with open(private_key_path, 'wb') as f:
            f.write(private_key.exportKey())

    if write_public:
        logging.info("Saving public global key to %s." % public_key_path)
        os.makedirs(os.path.dirname(public_key_path), exist_ok=True)
        with open(public_key_path, 'wb') as f:
            f.write(public_key.exportKey())

    return private_key, public_key
