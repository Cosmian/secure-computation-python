from cosmian_client_sgx.crypto.helper import seal, unseal


TEST_X25519_PUBKEY = bytes.fromhex("1f80306ddf75ee31bc8f71f29c93768bc6eaba2c1f67bcd7f179ca26d4361331")
TEST_X25519_PRIVKEY = bytes.fromhex("deb832a69e996898c835b9779c3a98cd3ba0b437a6aba94dacc33692154a815c")


def test_sealing():
    message: bytes = b"Hello World!"
    ciphertext: bytes = seal(message, TEST_X25519_PUBKEY)
    cleartext: bytes = unseal(ciphertext, TEST_X25519_PRIVKEY)

    assert message == cleartext
