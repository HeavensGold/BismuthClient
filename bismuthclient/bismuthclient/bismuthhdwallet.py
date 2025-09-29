"""
A class encapsulating a Bismuth HD wallet using BIP39 mnemonics and ECDSA cryptography
"""

import base64
import json
import logging
from typing import Optional, List, Dict
from os import path

from bismuth_bip39_tools.derivation import derive_addresses, check_mnemonic, mnemonic_to_seed
from bismuth_bip39_tools.mnemonic import generate_mnemonic
from bismuthclient.bismuth_ecdsa_crypto import BismuthECDSACrypto


class MnemonicMismatchException(Exception):
    """Raised when addresses in wallet file don't match the current mnemonic"""
    pass


class BismuthHDWallet:
    """
    HD wallet class that supports BIP39 mnemonics and ECDSA cryptography for Bismuth
    """
    
    __slots__ = ('_address', '_wallet_file', 'verbose', '_infos', 'key', 'public_key',
                 '_encrypted', '_current_index', '_derivation_path', '_mnemonic', '_seed',
                 '_derived_keys', '_addresses')

    def __init__(self, wallet_file: str = None, verbose: bool = False, password: str = "", mnemonic: str = ""):
        self._wallet_file = None
        self._address = None
        self._current_index = 0
        self._derivation_path = None
        self._mnemonic = None
        self._seed = None
        self._encrypted = False
        self.key = None  # private key hex
        self.public_key = ''  # public key hex
        self.verbose = verbose
        self._infos = None
        self._derived_keys = {}  # cache derived keys by index
        self._addresses = {}  # cache addresses by index

        if wallet_file:
            # Auto-generate wallet if it doesn't exist
            if not path.exists(wallet_file):
                if self.verbose:
                    print(f"HD wallet file {wallet_file} not found, creating new one")
                self.generate_new(wallet_file, word_count=24, password=password, label="Auto-generated HD Wallet", mnemonic=mnemonic)
            else:
                self.load(wallet_file, password)

    def wallet_preview(self, wallet_file: str = 'hd_wallet.json') -> dict:
        """
        Returns info about an HD wallet without actually loading it.
        """
        info = {'file': wallet_file, 'address': '', 'encrypted': False, 'type': 'HD-ECDSA', 'count': 0}
        try:
            with open(wallet_file, 'r') as f:
                content = json.load(f)
            
            if 'type' in content and content['type'] == 'HD-ECDSA':
                info['type'] = 'HD-ECDSA'
                info['encrypted'] = content.get('encrypted', False)
                if 'addresses' in content and isinstance(content['addresses'], list):
                    info['count'] = len(content['addresses'])
                    if content['addresses']:
                        info['address'] = content['addresses'][0].get('address', '')
                elif 'current_address' in content:
                    info['address'] = content['current_address']
        except Exception as e:
            if self.verbose:
                print(f"Error reading HD wallet preview {wallet_file}: {e}")
        
        return info

    def info(self) -> dict:
        """
        Returns a dict with info about the current wallet.
        """
        if not self._infos:
            self._infos = {
                "address": self._address,
                'file': self._wallet_file,
                'encrypted': self._encrypted,
                'type': 'HD-ECDSA',
                'current_index': self._current_index,
                'derivation_path': self._derivation_path
            }
        else:
            self._infos["address"] = self._address
        return self._infos

    def generate_new(self, wallet_file: str = 'hd_wallet.json', word_count: int = 24, 
                     password: str = "", label: str = "HD Wallet", mnemonic: str = "") -> bool:
        """
        Generate a new HD wallet with a new or existing mnemonic
        
        Args:
            wallet_file: Path to save the wallet
            word_count: Number of words in mnemonic (12 or 24) - ignored if mnemonic is provided
            password: Optional password to encrypt the wallet
            label: Label for the wallet
            mnemonic: Existing mnemonic to use (if empty, generates new one)
            
        Returns:
            True if successful, False otherwise
        """
        if path.exists(wallet_file):
            if self.verbose:
                print(f"Wallet file {wallet_file} already exists, not overwriting")
            return False
            
        if mnemonic:
            # Use provided mnemonic and validate it
            mnemonic = check_mnemonic(mnemonic)
        else:
            # Generate strength based on word count (128 for 12 words, 256 for 24 words)
            strength = 128 if word_count == 12 else 256 if word_count == 24 else 128
            if word_count not in [12, 24]:
                strength = 256  # default to 24 words
                
            # Generate new mnemonic
            mnemonic = generate_mnemonic(strength)
        
        # Save wallet with encrypted mnemonic if password provided
        if password:
            from bismuthclient.simplecrypt import encrypt
            encrypted_mnemonic = base64.b64encode(encrypt(password, mnemonic, level=1)).decode('utf-8')
            wallet_data = {
                'type': 'HD-ECDSA',
                'encrypted': True,
                'encrypted_mnemonic': encrypted_mnemonic,
                'current_index': 0,
                'label': label,
                'addresses': []
            }
            self._encrypted = True
        else:
            wallet_data = {
                'type': 'HD-ECDSA',
                'encrypted': False,
                'mnemonic': mnemonic,
                'current_index': 0,
                'label': label,
                'addresses': []
            }
            self._encrypted = False
            
        # Save to file
        with open(wallet_file, 'w') as f:
            json.dump(wallet_data, f, indent=4)
            
        if self.verbose:
            print(f"New HD wallet created: {wallet_file}")
            
        # Load the newly created wallet
        self.load(wallet_file, password)
        # Save again to populate the addresses array with the current address
        self.save()
        return True

    def load(self, wallet_file: str = 'hd_wallet.json', password: str = ""):
        """
        Load an HD wallet from file
        
        Args:
            wallet_file: Path to the wallet file
            password: Password for encrypted wallets
        """
        if self.verbose:
            print(f"Load HD Wallet {wallet_file}")
            
        self._wallet_file = wallet_file
        self._address = None
        self._current_index = 0
        
        with open(wallet_file, 'r') as f:
            content = json.load(f)
            
        self._encrypted = content.get('encrypted', False)
        
        if self._encrypted:
            if not password:
                raise ValueError("Wallet is encrypted, password required")
            from bismuthclient.simplecrypt import decrypt
            encrypted_mnemonic = content['encrypted_mnemonic']
            decoded = base64.b64decode(encrypted_mnemonic.encode('utf-8'))
            self._mnemonic = decrypt(password, decoded).decode('utf-8')
        else:
            self._mnemonic = content['mnemonic']
            
        # Validate mnemonic
        self._mnemonic = check_mnemonic(self._mnemonic)
        
        # Load current index
        self._current_index = content.get('current_index', 0)
        
        # Load seed
        self._seed = mnemonic_to_seed(self._mnemonic, password)
        
# Check if existing addresses in the file match the current mnemonic
        self._validate_addresses_match_mnemonic(content.get('addresses', []))
         
        # Set the current address to the first derived address
        self.set_address_index(self._current_index)
        
        # Update wallet file info
        self._wallet_file = wallet_file
        self._infos = {
            "address": self._address,
            'file': wallet_file,
            'encrypted': self._encrypted,
            'type': 'HD-ECDSA',
            'current_index': self._current_index,
            'derivation_path': self._derivation_path
        }

    def save(self, wallet_file: str = None):
        """
        Save the wallet state to file
        
        Args:
            wallet_file: Path to save to (defaults to loaded file)
        """
        if not wallet_file:
            wallet_file = self._wallet_file
            
        if not wallet_file:
            raise ValueError("No wallet file specified")
            
        # Load existing content to preserve other data
        if path.exists(wallet_file):
            with open(wallet_file, 'r') as f:
                content = json.load(f)
        else:
            content = {}
            
        # Update the current index
        content['current_index'] = self._current_index
        
        # Add current address to the addresses list if not present
        if 'addresses' not in content:
            content['addresses'] = []
            
        # Add current address if not already in the list
        current_addr_data = {
            'address': self._address,
            'index': self._current_index,
            'derivation_path': self._derivation_path,
            'timestamp': content.get('timestamp', int(__import__('time').time())),
            'label': content.get('label', 'HD Wallet')
        }
        
        # Check if address already exists in the list
        addr_exists = False
        for addr in content['addresses']:
            if addr['address'] == self._address:
                addr_exists = True
                # Update the index if it's the same address but different index
                if addr['index'] != self._current_index:
                    addr['index'] = self._current_index
                break
                
        if not addr_exists:
            content['addresses'].append(current_addr_data)
            
        # Sort addresses by index
        content['addresses'].sort(key=lambda x: x['index'])
        
        # Add type info if not present
        content['type'] = 'HD-ECDSA'
        content['encrypted'] = self._encrypted
        
        # Save to file
        with open(wallet_file, 'w') as f:
            json.dump(content, f, indent=4)

    def derive_address_at_index(self, index: int) -> Dict[str, str]:
        """
        Derive an address at a specific index
        
        Args:
            index: Index to derive address from
            
        Returns:
            Dictionary with address, private_key, public_key, and derivation_path
        """
        # Check if we already have this index cached
        if index in self._derived_keys:
            return self._derived_keys[index]
            
        # Derive the address
        addresses = derive_addresses(self._mnemonic, start=index, count=1)
        addr_data = addresses[0]
        
        # Cache the result
        self._derived_keys[index] = addr_data
        self._addresses[index] = addr_data['address']
        
        return addr_data

    def get_address_at_index(self, index: int) -> Dict[str, str]:
        """
        Get an address at a specific index and save it to the wallet file
        
        Args:
            index: Index to get address from
            
        Returns:
            Dictionary with address, private_key, public_key, and derivation_path
        """
        # Derive the address at the specified index
        addr_data = self.derive_address_at_index(index)
        
        # Update current state to the requested address
        self._current_index = index
        self._address = addr_data['address']
        self._derivation_path = addr_data['derivation_path']
        self.key = addr_data['private_key']
        self.public_key = addr_data['public_key']
        
        # Update info
        if self._infos:
            self._infos["address"] = self._address
            self._infos['current_index'] = self._current_index
            self._infos['derivation_path'] = self._derivation_path
            
        # Save the address to the wallet file if it's not already there
        self.save()
            
        return addr_data

    def fill_address_gaps(self) -> List[Dict[str, str]]:
        """
        Fill all gaps in the address sequence and save all missing addresses to the wallet file
        
        Returns:
            List of dictionaries with address data for all filled addresses
        """
        # Load current wallet file to get the existing addresses
        with open(self._wallet_file, 'r') as f:
            content = json.load(f)
            
        # Get existing addresses
        existing_addresses = content.get('addresses', [])
        if not existing_addresses:
            return []
            
        # Find the min and max indices
        indices = [addr['index'] for addr in existing_addresses]
        min_index = min(indices)
        max_index = max(indices)
        
        # Generate all addresses in the range
        filled_addresses = []
        for i in range(min_index, max_index + 1):
            # Check if this index already exists
            exists = any(addr['index'] == i for addr in existing_addresses)
            if not exists:
                # Generate and save the missing address
                addr_data = self.get_address_at_index(i)
                filled_addresses.append(addr_data)
                
        # Reload the current address (the one that was originally current)
        self.set_address_index(self._current_index)
        
        return filled_addresses

    def set_address_index(self, index: int):
        """
        Set the current address to the one at the specified index
        
        Args:
            index: Index to set as current address
        """
        addr_data = self.derive_address_at_index(index)
        
        self._current_index = index
        self._address = addr_data['address']
        self._derivation_path = addr_data['derivation_path']
        self.key = addr_data['private_key']  # private key hex
        self.public_key = addr_data['public_key']  # public key hex
        
        # Update info
        if self._infos:
            self._infos["address"] = self._address
            self._infos['current_index'] = self._current_index
            self._infos['derivation_path'] = self._derivation_path

    def get_new_address(self) -> Dict[str, str]:
        """
        Get a new unused address by incrementing the index
        
        Returns:
            Dictionary with address, private_key, public_key, and derivation_path
        """
        # Load current wallet file to get the latest state
        with open(self._wallet_file, 'r') as f:
            content = json.load(f)
            
        # Find the highest index in the existing addresses
        existing_addresses = content.get('addresses', [])
        if existing_addresses:
            max_index = max(addr['index'] for addr in existing_addresses)
            new_index = max_index + 1
        else:
            new_index = self._current_index + 1
            
        addr_data = self.derive_address_at_index(new_index)
        
        # Update current state to the new address
        self._current_index = new_index
        self._address = addr_data['address']
        self._derivation_path = addr_data['derivation_path']
        self.key = addr_data['private_key']
        self.public_key = addr_data['public_key']
        
        # Update info
        if self._infos:
            self._infos["address"] = self._address
            self._infos['current_index'] = self._current_index
            self._infos['derivation_path'] = self._derivation_path
            
        # Save the new address to the wallet file
        self.save()
            
        return addr_data

    @property
    def address(self) -> str:
        """Returns the currently loaded address, or None"""
        return self._address

    def sign_encoded(self, timestamp: float, address: str, recipient: str, 
                     amount: float, operation: str, data: str) -> str:
        """
        Sign a transaction using ECDSA
        
        Args:
            timestamp: Transaction timestamp
            address: Sender address
            recipient: Recipient address
            amount: Transaction amount
            operation: Operation type
            data: Additional data
            
        Returns:
            Base64 encoded signature
        """
        if address != self._address:
            raise RuntimeWarning(f"Address mismatch {address} vs {self._address}")
            
        signature = BismuthECDSACrypto.sign_transaction(
            timestamp, address, recipient, amount, operation, data, self.key
        )
        return signature

    def get_encoded_pubkey(self) -> str:
        """
        Returns the public key encoded as the network wants it
        
        Returns:
            Base64 encoded public key
        """
        if not self.public_key:
            return ''
        pubkey_bytes = bytes.fromhex(self.public_key)
        pubkey_b64 = base64.b64encode(pubkey_bytes).decode("utf-8")
        return pubkey_b64

    def get_mnemonic(self) -> str:
        """
        Get the wallet mnemonic (only if not encrypted)
        
        Returns:
            The mnemonic string
        """
        if self._encrypted:
            raise ValueError("Cannot access mnemonic of encrypted wallet without decrypting first")
        return self._mnemonic

    def get_derivation_path(self) -> str:
        """
        Get the current derivation path
        
        Returns:
            The derivation path string
        """
        return self._derivation_path

    def get_current_index(self) -> int:
        """
        Get the current address index
        
        Returns:
            Current index number
        """
        return self._current_index

    def get_all_derived_addresses(self, count: int = 10) -> List[Dict[str, any]]:
        """
        Get multiple derived addresses
        
        Args:
            count: Number of addresses to derive starting from index 0
            
        Returns:
            List of address dictionaries
        """
        addresses = derive_addresses(self._mnemonic, start=0, count=count)
        return addresses

    def _validate_addresses_match_mnemonic(self, existing_addresses: list):
        """
        Validate that existing addresses in the file match the current mnemonic.
        Raises MnemonicMismatchException if addresses don't match the current mnemonic.
        
        Args:
            existing_addresses: List of existing addresses from the file
            
        Raises:
            MnemonicMismatchException: When addresses in wallet file don't match current mnemonic
        """
        if not existing_addresses:
            return
            
        mismatched = []
        for addr_data in existing_addresses:
            index = addr_data.get('index')
            expected_address = addr_data.get('address')
            
            if index is not None and expected_address:
                # Derive the address at this index from the current mnemonic
                try:
                    derived_addresses = derive_addresses(self._mnemonic, start=index, count=1)
                    if derived_addresses:
                        derived_address = derived_addresses[0]['address']
                        if derived_address != expected_address:
                            mismatched.append((index, expected_address, derived_address))
                except Exception:
                    # If derivation fails, count as mismatch
                    mismatched.append((index, expected_address, "DERIVATION_FAILED"))
        
        if mismatched:
            mismatched_indices = [m[0] for m in mismatched]
            raise MnemonicMismatchException(
                f"Addresses in wallet file do not match current mnemonic. "
                f"Mismatched indices: {mismatched_indices}. "
                f"Use _clear_addresses_list() method to reset if intentional."
            )
    
    def _clear_addresses_list(self):
        """
        Clear the address list in the file and save it
        """
        # Load current wallet file to get the existing content
        if self._wallet_file and path.exists(self._wallet_file):
            try:
                with open(self._wallet_file, 'r') as f:
                    content = json.load(f)
                
                # Clear the addresses list
                content['addresses'] = []
                content['current_index'] = 0
                
                # Save the updated content
                with open(self._wallet_file, 'w') as f:
                    json.dump(content, f, indent=4)
                    
                print("Address list cleared in the file. Starting fresh with the current mnemonic.")
            except Exception as e:
                print(f"Error clearing address list: {e}")
