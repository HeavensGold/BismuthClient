# BismuthHDWallet New Methods Summary

## Overview
This document summarizes the new methods and improvements implemented in the `BismuthHDWallet` class to improve address management, security validation, workflow consistency, and mnemonic import capabilities.

## New Methods

### 1. `get_new_address()`
**Purpose**: Generate a new unused address by incrementing the index

**Location**: `BismuthHDWallet.py` (lines 305-332)

**Behavior**:
- Finds the highest index in the existing addresses
- Uses the next available index (highest index + 1)
- Derives the address at the new index
- Saves the new address to the wallet file
- Returns the address data dictionary

**Key Features**:
- Prevents index gaps by checking existing addresses
- Maintains sequential address generation
- Automatically saves to the wallet file

### 2. `get_address_at_index(index)`
**Purpose**: Get a specific address at a given index and save it to the wallet file

**Location**: `BismuthHDWallet.py` (lines 334-353)

**Behavior**:
- Derives the address at the specified index
- Updates the current address to the requested one
- Saves the address to the wallet file if not already present
- Returns the address data dictionary

**Key Features**:
- Fills gaps in the address sequence
- Allows direct access to any address index
- Handles address duplication prevention

### 3. `fill_address_gaps()`
**Purpose**: Fill all gaps in the address sequence and save all missing addresses

**Location**: `BismuthHDWallet.py` (lines 355-379)

**Behavior**:
- Finds the minimum and maximum indices in the address list
- Generates all addresses in the range
- Saves missing addresses to the wallet file
- Returns list of filled addresses

**Key Features**:
- Automatically detects and fills gaps
- Maintains sequential address order
- Handles large address ranges efficiently

### 4. `_validate_addresses_match_mnemonic(existing_addresses)`
**Purpose**: Validate that existing addresses in the file match the current mnemonic

**Location**: `BismuthHDWallet.py` (lines 538-568)

**Behavior**:
- Checks if addresses can be regenerated from the current mnemonic
- Displays warning for mismatched addresses
- Requests user confirmation before clearing
- Clears address list and resets index only if confirmed

**Key Features**:
- **Critical Security Feature**: Prevents mixing addresses from different mnemonic seeds
- User confirmation required before clearing
- Immediate program termination if user doesn't confirm
- Clear warning messages about mismatched addresses

### 5. `_clear_addresses_list()`
**Purpose**: Clear the address list in the file

**Location**: `BismuthHDWallet.py` (lines 570-586)

**Behavior**:
- Loads current wallet file
- Clears the addresses array
- Resets the current index to 0
- Saves the updated file

**Key Features**:
- Clean slate for new mnemonic operations
- Preserves other wallet metadata

## Enhanced Workflow

### 1. **Address Sorting**
- Modified `save()` method to automatically sort addresses by index
- Addresses are always stored in sequential order: `[0, 1, 2, 3]` instead of `[0, 2, 3, 1]`

### 2. **Security Validation**
- Added validation during wallet loading to detect mnemonic mismatches
- Prevents dangerous scenario where addresses from different seeds could be mixed

### 3. **Gap Handling**
- Both `get_new_address()` and `fill_address_gaps()` handle missing indices
- Ensures addresses are generated in sequence without gaps

## Usage Examples

```python
from bismuthclient.bismuthhdwallet import BismuthHDWallet

# Load wallet
wallet = BismuthHDWallet('test_hd_wallet.json')

# Get new address (sequential)
new_addr = wallet.get_new_address()

# Get specific address
specific_addr = wallet.get_address_at_index(5)

# Fill gaps in address sequence
filled_addresses = wallet.fill_address_gaps()

# Security validation happens automatically during loading
# If mnemonic mismatch detected, user will be prompted
```

## Security Improvements

The new methods address critical security concerns:

1. **Prevents Address Mixing**: No accidental mixing of addresses from different mnemonic seeds
2. **User Confirmation**: Clear warnings and user consent required before destructive operations
3. **Data Integrity**: Addresses are always validated against the current mnemonic
4. **Sequential Generation**: Addresses are generated in order, preventing gaps and inconsistencies

## File Structure Changes

The wallet file now maintains addresses in sorted order:

```json
{
    "type": "HD-ECDSA",
    "encrypted": false,
    "mnemonic": "...",
    "current_index": 0,
    "addresses": [
        {"address": "Bis1...", "index": 0, ...},
        {"address": "Bis1...", "index": 1, ...},
        {"address": "Bis1...", "index": 2, ...}
    ]
}
```

## Latest Updates (Library-Safe Error Handling & Mnemonic Import)

### 6. `MnemonicMismatchException`
**Purpose**: Custom exception for library-safe error handling when addresses don't match mnemonic

**Location**: `bismuthhdwallet.py` (line 18)

**Key Features**:
- **Library-appropriate**: Replaces interactive prompts and `sys.exit()` calls
- **Specific exception type**: Allows client applications to catch and handle mnemonic mismatches programmatically
- **Clear error messages**: Provides actionable information about which indices are mismatched
- **Follows existing patterns**: Consistent with `DecryptionException` and `EncryptionException` in the codebase

### 7. Enhanced `_validate_addresses_match_mnemonic()`
**Purpose**: Library-safe validation that raises exceptions instead of interactive prompts

**Location**: `BismuthHDWallet.py` (lines 510-542)

**Behavior Changes**:
- **Before**: Used `input()` prompts and `sys.exit(1)` - inappropriate for library use
- **After**: Raises `MnemonicMismatchException` with detailed error information
- **Error message includes**: List of mismatched indices and guidance on resolution

**Key Features**:
- **Non-blocking**: No interactive prompts that halt execution
- **Programmatic handling**: Client applications can catch and handle errors appropriately
- **Detailed diagnostics**: Clear information about what went wrong and how to fix it

### 8. Enhanced `load_hd_wallet()` Method (BismuthClient)
**Purpose**: Support importing mnemonics from other wallet applications

**Location**: `bismuthclient.py` (lines 432-455)

**New Signature**:
```python
def load_hd_wallet(self, wallet_file='hd_wallet.json', password: str = "", mnemonic: str = "")
```

**Behavior**:
- **Mnemonic parameter**: When provided, uses existing mnemonic instead of generating new one
- **Import capability**: Enables importing wallets from MetaMask, Electrum, and other BIP39-compatible applications
- **Fallback logic**: If no mnemonic provided, behaves exactly as before (backward compatible)

### 9. Enhanced `BismuthHDWallet.__init__()`
**Purpose**: Support mnemonic parameter in wallet initialization

**Location**: `BismuthHDWallet.py` (lines 28-52)

**New Signature**:
```python
def __init__(self, wallet_file: str = None, verbose: bool = False, password: str = "", mnemonic: str = "")
```

**Key Features**:
- **Mnemonic passthrough**: Forwards mnemonic parameter to `generate_new()` method
- **Maintains compatibility**: All existing code continues to work unchanged

### 10. Enhanced `generate_new()` Method
**Purpose**: Support creating wallets with existing mnemonics

**Location**: `BismuthHDWallet.py` (lines 95-119)

**New Signature**:
```python
def generate_new(self, wallet_file: str = 'hd_wallet.json', word_count: int = 24, 
                 password: str = "", label: str = "HD Wallet", mnemonic: str = "") -> bool
```

**Behavior**:
- **Mnemonic validation**: If mnemonic provided, validates it using `check_mnemonic()`
- **Generation fallback**: If no mnemonic provided, generates new one based on `word_count`
- **Import workflow**: Enables creating wallets with mnemonics from external sources

## Error Handling Improvements

### Before (Library-Unsafe)
```python
print("WARNING: Some addresses in the wallet file do not match the current mnemonic!")
print("Please confirm this action (type 'yes' to proceed):")
user_input = input().strip().lower()
if user_input != 'yes':
    import sys
    sys.exit(1)
```

### After (Library-Safe)
```python
raise MnemonicMismatchException(
    f"Addresses in wallet file do not match current mnemonic. "
    f"Mismatched indices: {mismatched_indices}. "
    f"Use _clear_addresses_list() method to reset if intentional."
)
```

## Import Workflow Examples

### Importing from External Wallet
```python
from bismuthclient.bismuthclient import BismuthClient
from bismuthclient.bismuthhdwallet import MnemonicMismatchException

# Import mnemonic from MetaMask/Electrum/etc.
external_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

try:
    client = BismuthClient()
    client.load_hd_wallet('imported_wallet.json', password="", mnemonic=external_mnemonic)
    print(f"Successfully imported wallet: {client.address}")
except Exception as e:
    print(f"Import failed: {e}")
```

### Handling Mnemonic Mismatches
```python
try:
    client = BismuthClient()
    client.load_hd_wallet('existing_wallet.json')
except MnemonicMismatchException as e:
    print(f"Mnemonic mismatch detected: {e}")
    # Client application decides what to do:
    # - Prompt user to confirm clearing addresses
    # - Load with different mnemonic
    # - Show error and abort
    # - Automatically clear and proceed (if appropriate)
```

## Backward Compatibility

These changes maintain full backward compatibility with existing HD wallet files while adding new security features and import capabilities. Existing wallets will continue to work with the enhanced validation and management capabilities, but now with proper library-safe error handling.