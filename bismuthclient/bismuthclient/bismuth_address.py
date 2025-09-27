"""
Bismuth Bis1 Address Generation Module

This module handles ECDSA-based Bis1 address generation using the secp256k1 curve.
Bis1 addresses are the new ECDSA format for Bismuth blockchain.
"""

import hashlib
import base58
from typing import Tuple, Optional
from polysign.signer import SignerType, SignerSubType
from polysign.signerfactory import SignerFactory


class BismuthAddress:
    """
    Bismuth Bis1 address generation and validation.

    Bis1 addresses use ECDSA secp256k1 curve with Base58Check encoding.
    """

    # Network prefixes for different environments (from official spec)
    MAINNET_PREFIX = b'\x4f\x54\x5b'      # Bismuth mainnet prefix
    TESTNET_PREFIX = b'\x01\x7a\xb6\x85'  # Testnet addresses

    @staticmethod
    def generate_keypair() -> Tuple[str, str, str]:
        """
        Generate a new ECDSA keypair and return private key, public key, and address.

        Returns:
            Tuple[str, str, str]: (private_key_hex, public_key_hex, bis1_address)
        """
        # Generate new ECDSA key using ecdsa library directly
        import secrets
        from ecdsa import SigningKey, SECP256k1

        # Generate a random private key
        private_key_int = secrets.randbits(256)
        private_key_hex = f"{private_key_int:064x}"

        # Create signing key from private key
        sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)

        # Get compressed public key
        vk = sk.get_verifying_key()
        public_key_hex = vk.to_string("compressed").hex()

        # Generate Bis1 address
        bis1_address = BismuthAddress.public_key_to_bis1(public_key_hex)

        return private_key_hex, public_key_hex, bis1_address

    @staticmethod
    def private_key_to_public_key(private_key_hex: str) -> str:
        """
        Convert private key to public key.

        Args:
            private_key_hex: Private key in hex format

        Returns:
            str: Public key in hex format
        """
        from ecdsa import SigningKey, SECP256k1

        # Create signing key from private key hex
        sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)

        # Get compressed public key
        vk = sk.get_verifying_key()
        public_key_hex = vk.to_string("compressed").hex()

        return public_key_hex

    @staticmethod
    def private_key_to_bis1(private_key_hex: str) -> str:
        """
        Convert private key to Bis1 address.

        Args:
            private_key_hex: Private key in hex format

        Returns:
            str: Bis1 address
        """
        public_key_hex = BismuthAddress.private_key_to_public_key(private_key_hex)
        return BismuthAddress.public_key_to_bis1(public_key_hex)

    @staticmethod
    def public_key_to_bis1(public_key_hex: str, network_prefix: bytes = None) -> str:
        """
        Convert public key to Bis1 address using Base58Check encoding.
        Follows the official Bismuth specification.

        Args:
            public_key_hex: Public key in hex format (compressed or uncompressed)
            network_prefix: Network prefix bytes (default: MAINNET_PREFIX)

        Returns:
            str: Bis1 address
        """
        if network_prefix is None:
            network_prefix = BismuthAddress.MAINNET_PREFIX

        try:
            # Convert hex public key to bytes
            public_key_bytes = bytes.fromhex(public_key_hex)

            # Create SHA256 hash of public key
            sha256_hash = hashlib.sha256(public_key_bytes).digest()

            # Create RIPEMD160 hash of the SHA256 hash
            ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

            # Add network prefix
            prefixed_hash = network_prefix + ripemd160_hash

            # Use Base58Check encoding (includes automatic checksum)
            bis1_address = base58.b58encode_check(prefixed_hash).decode('utf-8')

            return bis1_address

        except Exception as e:
            raise ValueError(f"Invalid public key format: {e}")

    @staticmethod
    def validate_bis1_address(address: str) -> bool:
        """
        Validate a Bis1 address format and checksum.

        Args:
            address: Bis1 address string

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Decode Base58Check (automatically validates checksum)
            decoded = base58.b58decode_check(address)

            # Check if it has the correct Bismuth network prefix
            if not decoded.startswith(BismuthAddress.MAINNET_PREFIX):
                # Could be testnet
                if not decoded.startswith(BismuthAddress.TESTNET_PREFIX):
                    return False

            # Should have prefix + 20-byte RIPEMD160 hash
            expected_length = len(BismuthAddress.MAINNET_PREFIX) + 20
            if len(decoded) != expected_length and len(decoded) != len(BismuthAddress.TESTNET_PREFIX) + 20:
                return False

            return True

        except Exception:
            return False

    @staticmethod
    def is_bis1_address(address: str) -> bool:
        """
        Check if an address is a Bis1 format address.

        Args:
            address: Address string to check

        Returns:
            bool: True if it's a Bis1 address format
        """
        # Bis1 addresses should start with 'Bis1' for mainnet
        if not address.startswith('Bis1'):
            return False

        # Validate the full address format
        return BismuthAddress.validate_bis1_address(address)

    @staticmethod
    def get_address_type(address: str) -> str:
        """
        Determine the type of Bismuth address.

        Args:
            address: Address string

        Returns:
            str: 'bis1' for ECDSA addresses, 'legacy' for RSA addresses, 'invalid' for invalid
        """
        if BismuthAddress.is_bis1_address(address):
            return 'bis1'
        elif BismuthAddress.is_legacy_address(address):
            return 'legacy'
        else:
            return 'invalid'

    @staticmethod
    def is_legacy_address(address: str) -> bool:
        """
        Check if an address is a legacy RSA format address.

        Args:
            address: Address string to check

        Returns:
            bool: True if it's a legacy RSA address format
        """
        # Legacy addresses are typically 56 characters long and contain only alphanumeric + some symbols
        if len(address) < 50 or len(address) > 60:
            return False

        # Legacy addresses don't start with 'Bis1'
        if address.startswith('Bis1'):
            return False

        # Basic character validation for legacy addresses
        import re
        return bool(re.match(r'^[A-Za-z0-9+/=]+$', address))


def generate_new_address() -> dict:
    """
    Convenience function to generate a new Bis1 address with all associated data.

    Returns:
        dict: Dictionary containing private_key, public_key, address, and type
    """
    private_key, public_key, address = BismuthAddress.generate_keypair()

    return {
        'type': 'ECDSA',
        'curve': 'secp256k1',
        'private_key': private_key,
        'public_key': public_key,
        'address': address,
        'compressed': True,  # polysign uses compressed public keys by default
        'network': 'mainnet'
    }


if __name__ == "__main__":
    # Example usage
    print("Generating new Bis1 address...")
    addr_data = generate_new_address()

    print(f"Private Key: {addr_data['private_key']}")
    print(f"Public Key:  {addr_data['public_key']}")
    print(f"Address:     {addr_data['address']}")
    print(f"Valid:       {BismuthAddress.validate_bis1_address(addr_data['address'])}")
    print(f"Type:        {BismuthAddress.get_address_type(addr_data['address'])}")