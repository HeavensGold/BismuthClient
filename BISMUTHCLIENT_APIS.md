# BismuthClient API Reference

## Main APIs and Callable Functions

### 1. **BismuthClient Class** (main interface) - `bismuthclient.py`
- `__init__(servers_list, app_log, loop, wallet_file, verbose)` - Initialize the client
- `balance(for_display=False)` - Get current address balance
- `global_balance(for_display=False)` - Get balance for all addresses in multiwallet
- `all_balances(for_display=False)` - Get balances for every address in multiwallet
- `latest_transactions(num=10, offset=0, for_display=False, mempool_included=False)` - Get recent transactions
- `send(recipient, amount, operation='', data='', error_reply=[])` - Send a transaction
- `sign(message)` - Sign a message
- `encrypt(message, recipient)` - Encrypt a message for a recipient
- `decrypt(message)` - Decrypt a message
- `status()` - Get current server status
- `load_wallet(wallet_file)` - Load a wallet file
- `load_multi_wallet(wallet_file)` - Load a multiwallet file
- `load_hd_wallet(wallet_file, password='')` - Load an HD wallet file
- `new_wallet(wallet_file)` - Create a new wallet
- `set_address(address='')` - Set current address (for multiwallet)
- `wallet(full=False)` - Get info about current wallet
- `info()` - Get client info (wallet, address, server, etc.)
- `get_server()` - Find and connect to best server
- `set_server(ipport)` - Connect to specific server
- `refresh_server_list()` - Refresh server list from API
- `command(command, options=None)` - Send raw command to server
- `list_wallets(scan_dir='wallets')` - List wallet files in directory
- `set_alias_cache_file(filename)` - Set file for persistent alias cache
- `get_aliases_of(addresses)` - Get aliases for a list of addresses
- `has_alias(address)` - Check if address has alias
- `alias_exists(alias)` - Check if alias exists
- `clear_cache()` - Clear internal cache

### 2. **BismuthWallet Class** (wallet management) - `bismuthwallet.py`
- `__init__(wallet_file, verbose)` - Initialize wallet
- `load(wallet_file)` - Load wallet file
- `new(wallet_file)` - Create new wallet file
- `wallet_preview(wallet_file)` - Get wallet info without loading
- `info()` - Get wallet information
- `sign_encoded(timestamp, address, recipient, amount, operation, data)` - Sign transaction
- `get_encoded_pubkey()` - Get encoded public key
- `address` (property) - Get current address

### 3. **BismuthMultiWallet Class** (multiwallet support) - `bismuthmultiwallet.py`
- `__init__(wallet_file, verbose, seed)` - Initialize multiwallet
- `load(wallet_file, seed)` - Load multiwallet file
- `save(wallet_file)` - Save multiwallet
- `new_address(label='', password='', salt='', type)` - Add new address to wallet
- `set_label(address='', label='')` - Set label for address
- `set_spend(spend_type, spend_value, password='')` - Set spend protection
- `import_der(wallet_der, label='', source_password='')` - Import legacy wallet
- `import_ecdsa_pk(private_key, label='')` - Import ECDSA private key
- `import_hd_address(hd_wallet, address_index, label='')` - Import HD wallet address
- `encrypt(password='', current_password=None)` - Encrypt wallet
- `lock()` - Lock the wallet
- `unlock(password)` - Unlock the wallet
- `password_ok(password)` - Check password validity
- `get_key(address='')` - Get key for address
- `set_address(address=''))` - Set current address
- `is_address_in_wallet(address='')` - Check if address exists in wallet
- `sign_encoded(timestamp, address, recipient, amount, operation, data)` - Sign transaction
- `get_encoded_pubkey()` - Get encoded public key
- `address` (property) - Get current address

### 4. **Crypto Functions** - `bismuthcrypto.py`
- `sign_with_key(timestamp, address, recipient, amount, operation, openfield, key)` - Sign with RSA key
- `sign_with_ecdsa_key(timestamp, address, recipient, amount, operation, openfield, key)` - Sign with ECDSA
- `sign_message_with_key(message, key)` - Sign message
- `encrypt_message_with_pubkey(message, pubkey)` - Encrypt message
- `decrypt_message_with_key(message, key)` - Decrypt message
- `keys_new(keyfile)` - Create new keys
- `keys_gen(password, salt, count, verbose)` - Generate deterministic keys
- `stringify_transaction(timestamp, address, recipient, amount, operation, openfield)` - Format transaction
- `address_validate(address)` - Validate address format
- `ecdsa_pk_to_signer(private_key)` - Create ECDSA signer

### 5. **Connection Functions** - `rpcconnections.py`
- `Connection(ipport, verbose=False, raw=False)` - Connection class
- `command(command, options=None)` - Send command to server
- `check_connection()` - Check connection state
- `close()` - Close connection

### 6. **Formatting Functions** - `bismuthformat.py`
- `TxFormatter(tx).to_json(for_display=False)` - Format transaction to JSON
- `AmountFormatter(amount).to_string(decimals=3, leading=0)` - Format amount

### 7. **API Functions** - `bismuthapi.py`
- `get_wallet_servers_legacy(light_ip_list='', app_log=None, minver='0', as_dict=False)` - Get wallet server list from API

### 8. **BismuthHDWallet Class** (HD wallet support) - `bismuthhdwallet.py`
- `__init__(wallet_file, verbose, password)` - Initialize HD wallet
- `generate_new(wallet_file, word_count=12, password='', label='HD Wallet')` - Generate new HD wallet
- `load(wallet_file, password='')` - Load HD wallet file
- `save(wallet_file)` - Save HD wallet state
- `derive_address_at_index(index)` - Derive address at specific index
- `set_address_index(index)` - Set current address to index
- `get_new_address()` - Get next unused address
- `get_mnemonic()` - Get wallet mnemonic (unencrypted wallets only)
- `get_derivation_path()` - Get current derivation path
- `get_current_index()` - Get current address index
- `get_all_derived_addresses(count=10)` - Get multiple derived addresses
- `sign_encoded(timestamp, address, recipient, amount, operation, data)` - Sign transaction
- `get_encoded_pubkey()` - Get encoded public key
- `wallet_preview(wallet_file)` - Get HD wallet info without loading
- `info()` - Get HD wallet information
- `address` (property) - Get current address

### 9. **BismuthECDSACrypto Class** (ECDSA cryptography) - `bismuth_ecdsa_crypto.py`
- `sign_transaction(timestamp, address, recipient, amount, operation, data, private_key)` - Sign transaction with ECDSA
- `verify_signature(signature, message, public_key)` - Verify ECDSA signature
- `generate_keypair()` - Generate new ECDSA keypair
- `private_key_to_public(private_key)` - Get public key from private key
- `public_key_to_address(public_key)` - Convert public key to Bis1 address

### 10. **Address Utilities** - `bismuth_address.py`
- `validate_bis1_address(address)` - Validate Bis1 address format
- `pubkey_to_bis1_address(public_key_hex)` - Convert public key to Bis1 address
- `is_valid_address_format(address)` - Check address format validity

### 11. **Async Client** (future use) - `async_client.py`
- `AsyncClient(server_list, app_log, loop, address)` - Async client class
- `command(data, param=None, timeout=None)` - Send async command
- `send(data, timeout=None)` - Send async data
- `receive(timeout=None)` - Receive async data

These APIs provide comprehensive functionality for:
- **Wallet management**: create, load, multiwallet support, HD wallets
- **HD Wallet support**: BIP39/BIP44 compliant hierarchical deterministic wallets
- **Transaction operations**: send, check balance, history
- **Cryptographic operations**: RSA/ECDSA signing, encryption/decryption
- **Address management**: Bis1 format, validation, derivation
- **Network communication**: connection to Bismuth nodes
- **Server discovery**: automatic server selection and management
- **Transaction formatting**: display and JSON conversion

## Main Integration Points

The main entry points for users are:
- **`BismuthClient`** - Primary interface for all wallet and transaction operations
- **`BismuthHDWallet`** - HD wallet creation and management (BIP39/BIP44)
- **`BismuthMultiWallet`** - Multi-address wallet management with HD support
- **`BismuthWallet`** - Single address legacy wallet support

## HD Wallet Features

The HD wallet implementation provides:
- **Standards compliance**: BIP39 mnemonics, BIP44 derivation paths
- **Mnemonic support**: 12-word (128-bit) and 24-word (256-bit) seed phrases
- **Derivation path**: `m/44'/209'/0'/0/n` (Bismuth coin type 209)
- **Address format**: Bis1 addresses using ECDSA secp256k1 + RIPEMD-160
- **Security**: Optional password encryption for wallet files
- **Integration**: Full compatibility with existing BismuthClient ecosystem