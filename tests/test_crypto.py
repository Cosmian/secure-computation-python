from cosmian_client_sgx.crypto.helper import *

from keys import *


def test_encrypt():
    message: bytes = b"Hello World!"

    assert (len(CP_SYMKEY) == len(DP1_SYMKEY) ==
            len(DP2_SYMKEY) == len(RC_SYMKEY) == 32)

    ciphertext: bytes = encrypt(message, CP_SYMKEY)
    cleartext: bytes = decrypt(ciphertext, CP_SYMKEY)
    assert message == cleartext


def test_sealing():
    message: bytes = b"Hello World!"

    assert (len(CP_PUBKEY) == len(DP1_PUBKEY) ==
            len(DP2_PUBKEY) == len(RC_PUBKEY) == 32)
    assert (len(CP_PRIVKEY) == len(DP1_PRIVKEY) ==
            len(DP2_PRIVKEY) == len(RC_PRIVKEY) == 32)

    ciphertext: bytes = seal(message, CP_PUBKEY)
    cleartext: bytes = unseal(ciphertext, CP_PRIVKEY)
    assert message == cleartext

    ciphertext: bytes = seal(message, DP1_PUBKEY)
    cleartext: bytes = unseal(ciphertext, DP1_PRIVKEY)
    assert message == cleartext

    ciphertext: bytes = seal(message, DP2_PUBKEY)
    cleartext: bytes = unseal(ciphertext, DP2_PRIVKEY)
    assert message == cleartext

    ciphertext: bytes = seal(message, RC_PUBKEY)
    cleartext: bytes = unseal(ciphertext, RC_PRIVKEY)
    assert message == cleartext
