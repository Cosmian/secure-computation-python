"""cosmian_client_sgx.cli.main module."""

import argparse

from cosmian_client_sgx.cli.encrypt import parse_encrypt
from cosmian_client_sgx.cli.decrypt import parse_decrypt


def main() -> int:
    # top-level parsers
    parser = argparse.ArgumentParser(
        description="Cosmian Util CLI for Secure Computation")
    subparsers = parser.add_subparsers(help="sub-command")

    # parser for "encrypt" command
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt file or directory")
    enc_out_group = encrypt_parser.add_mutually_exclusive_group()
    enc_out_group.add_argument("--directory",
                               help="Directory path to encrypt all files")
    enc_out_group.add_argument("--file",
                               help="File path to encrypt")
    enc_key_group = encrypt_parser.add_mutually_exclusive_group()
    enc_key_group.add_argument("--key",
                               help="Symmetric secret key for encryption")
    enc_key_group.add_argument("--key-file",
                               help="Symmetric secret key file path for encryption")
    encrypt_parser.add_argument("--tar",
                                help="Create a tar file with encrypted files",
                                action="store_true")
    encrypt_parser.add_argument("--output-dir",
                                help="Output directory (default to .)",
                                default=".")
    encrypt_parser.set_defaults(func=parse_encrypt)

    # parser for "decrypt" command
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt file or directory")
    dec_out_group = decrypt_parser.add_mutually_exclusive_group()
    dec_out_group.add_argument("--directory",
                               help="Directory path to decrypt all files")
    dec_out_group.add_argument("--file",
                               help="File path to decrypt")
    dec_key_group = decrypt_parser.add_mutually_exclusive_group()
    dec_key_group.add_argument("--key",
                               help="Symmetric secret key for decryption")
    dec_key_group.add_argument("--key-file",
                               help="Symmetric secret key file path for decryption")
    decrypt_parser.add_argument("--output-dir",
                                help="Output directory (default to .)",
                                default=".")
    decrypt_parser.set_defaults(func=parse_decrypt)

    args = parser.parse_args()
    args.func(args)

    return 0
