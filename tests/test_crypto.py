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

    assert (len(CP_X25519_PUBKEY) == len(DP1_X25519_PUBKEY) ==
            len(DP2_X25519_PUBKEY) == len(RC_X25519_PUBKEY) == 32)
    assert (len(CP_X25519_PRIVKEY) == len(DP1_X25519_PRIVKEY) ==
            len(DP2_X25519_PRIVKEY) == len(RC_X25519_PRIVKEY) == 32)

    ciphertext: bytes = seal(message, CP_X25519_PUBKEY)
    cleartext: bytes = unseal(ciphertext, CP_X25519_PRIVKEY)
    assert message == cleartext

    ciphertext: bytes = seal(message, DP1_X25519_PUBKEY)
    cleartext: bytes = unseal(ciphertext, DP1_X25519_PRIVKEY)
    assert message == cleartext

    ciphertext: bytes = seal(message, DP2_X25519_PUBKEY)
    cleartext: bytes = unseal(ciphertext, DP2_X25519_PRIVKEY)
    assert message == cleartext

    ciphertext: bytes = seal(message, RC_X25519_PUBKEY)
    cleartext: bytes = unseal(ciphertext, RC_X25519_PRIVKEY)
    assert message == cleartext


def test_sign():
    assert (len(CP_ED25519_PUBKEY) == len(DP1_ED25519_PUBKEY) ==
            len(DP2_ED25519_PUBKEY) == len(RC_ED25519_PUBKEY) == 32)
    assert (len(CP_ED25519_PRIVKEY) == len(DP1_ED25519_PRIVKEY) ==
            len(DP2_ED25519_PRIVKEY) == len(RC_ED25519_PRIVKEY) == 32)
    assert (len(CP_ED25519_SEED) == len(DP1_ED25519_SEED) ==
            len(DP2_ED25519_SEED) == len(RC_ED25519_SEED) == 32)

    test_keys: List[Tuple[bytes, bytes, bytes]] = [
        (CP_SYMKEY, CP_ED25519_SEED, CP_ED25519_PUBKEY),
        (DP1_SYMKEY, DP1_ED25519_SEED, DP1_ED25519_PUBKEY),
        (DP2_SYMKEY, DP2_ED25519_SEED, DP2_ED25519_PUBKEY),
        (RC_SYMKEY, RC_ED25519_SEED, RC_ED25519_PUBKEY)
    ]

    for (msg, sk, pk) in test_keys:
        sig: bytes = sign(msg, sk)
        assert verify(msg, sig, pk) is True


def test_sig_and_seal():
    enclave_ed25519_pk, enclave_ed25519_seed, enclave_ed25519_sk = ed25519_keygen()
    enclave_x25519_pk, enclave_x25519_sk = ed25519_to_x25519_keypair(
        enclave_ed25519_pk,
        enclave_ed25519_seed
    )

    sig: bytes = sign(DP1_SYMKEY, DP1_ED25519_SEED)

    sealed_symkey: bytes = seal(sig + DP1_SYMKEY, enclave_x25519_pk)

    assert len(sealed_symkey) == 144

    unsealed_symkey: bytes = unseal(sealed_symkey, enclave_x25519_sk)

    assert len(unsealed_symkey) == 64 + 32

    assert verify(unsealed_symkey[64:], unsealed_symkey[:64], DP1_ED25519_PUBKEY) is True
