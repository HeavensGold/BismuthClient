# `load_multi_wallet()` Workflow Analysis

This document outlines the process of loading a multi-wallet using the `load_multi_wallet()` function in the Bismuth client, with a special focus on the creation of a new `wallet.json` file when one is not found.

## Overview

The `load_multi_wallet()` function is part of the `BismuthClient` class and is responsible for loading a `wallet.json` file that can contain multiple Bismuth addresses. If the specified wallet file does not exist, the client is designed to create a new one automatically.

## Workflow Breakdown

1.  **Initiation**: The process begins when the `load_multi_wallet(wallet_file='wallet.json')` method is called on a `BismuthClient` instance.

2.  **`BismuthMultiWallet` Instantiation**: Inside `load_multi_wallet()`, a `BismuthMultiWallet` object is created. The path to the `wallet.json` file is passed to its constructor. This is the key step where the wallet is either loaded or created.

3.  **File Existence Check**: The `BismuthMultiWallet` class's `__init__` method calls its `load` method. The `load` method, located in `bismuthclient/bismuthmultiwallet.py`, checks if the provided `wallet_file` path exists using `os.path.isfile()`.

4.  **`wallet.json` Creation**: If the file does not exist, the `load` method executes a code block to create a new `wallet.json` file. This involves:
    *   Generating a random salt.
    *   Creating a default dictionary structure containing the salt, version information, and an empty list for addresses.
    *   Writing this dictionary to the new `wallet.json` file in JSON format.

    The code responsible for this is:
    ```python
    if not path.isfile(wallet_file):
        charset = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&~#{([|-\_@)]=}+-*/<>!,;:.?%'
        salt = "".join(random.choice(charset) for x in range(random.randint(10, 20)))
        default = {"salt": salt, "spend": {"type": None, "value": None},
                   "version": __version__, "coin": "bis", "encrypted": False,
                   "addresses": []}
        with open(wallet_file, 'w') as f:
            json.dump(default, f)
    ```

5.  **Initial Address Creation**: After the `BismuthMultiWallet` object is created (and a new `wallet.json` is potentially created), the `load_multi_wallet` method in `bismuthclient.py` checks if the wallet contains any addresses. For a newly created wallet, the "addresses" list will be empty.

6.  **Default Address**: If the wallet has no addresses, the `load_multi_wallet` method calls `self._wallet.new_address(label="default")` to generate a new Bismuth address and add it to the wallet. This ensures that a new wallet is not empty and is ready for use.

## Summary

The `load_multi_wallet()` workflow is designed to be seamless. It abstracts away the need for a manual check for the existence of a wallet file. If a wallet is not present, a new one is created with a default address, providing a smooth user experience.
