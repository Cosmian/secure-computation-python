from cosmian_secure_computation_client.crypto.helper import *

from keys import *


def test_encrypt():
    message: bytes = b"Hello World!"

    assert (len(CP_SYMKEY) == len(DP1_SYMKEY) ==
            len(DP2_SYMKEY) == len(RC_SYMKEY) == 32)

    ciphertext: bytes = encrypt(message, CP_SYMKEY)
    cleartext: bytes = decrypt(ciphertext, CP_SYMKEY)
    assert message == cleartext


def test_seal():
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


def test_sign():
    public_key, seed, _ = ed25519_keygen()

    message: bytes = b"Hello World!"

    sig: bytes = sign(message, seed)

    assert verify(message, sig, public_key) is True


def test_verify():
    enclave_public_key, enclave_seed, _ = ed25519_keygen()
    enclave_x25519_pk, enclave_x25519_sk = ed25519_to_x25519(
        enclave_public_key,
        enclave_seed
    )

    client_public_key, client_seed, _ = ed25519_keygen()

    symkey: bytes = random_symkey()
    sig: bytes = sign(symkey, client_seed)

    sealed_symkey: bytes = seal(sig + symkey, enclave_x25519_pk)

    assert len(sealed_symkey) == 144

    unsealed_symkey: bytes = unseal(sealed_symkey, enclave_x25519_sk)

    assert len(unsealed_symkey) == 64 + 32

    assert verify(unsealed_symkey[64:], unsealed_symkey[:64], client_public_key) is True
