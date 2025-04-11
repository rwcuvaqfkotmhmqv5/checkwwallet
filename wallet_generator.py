"""
Wallet generator module for the cryptocurrency brute force tool.
Handles the creation of wallet addresses from seed phrases using BIP standards.
"""

import logging
from bip_utils import (
    Bip39SeedGenerator, 
    Bip44, 
    Bip44Coins,
    Bip44Changes,
    Bip39MnemonicValidator
)

def validate_mnemonic(mnemonic):
    """
    Validate if a mnemonic phrase is valid according to BIP-39 standard.
    
    Args:
        mnemonic (str): The mnemonic phrase to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        return Bip39MnemonicValidator().IsValid(mnemonic)
    except Exception as e:
        logging.error(f"Error validating mnemonic: {str(e)}")
        return False

def generate_addresses(mnemonic, account_idx=0, address_idx=0):
    """
    Generate cryptocurrency addresses from a BIP-39 mnemonic.
    
    Args:
        mnemonic (str): BIP-39 mnemonic seed phrase
        account_idx (int): Account index (default: 0)
        address_idx (int): Address index (default: 0)
        
    Returns:
        dict: Dictionary of addresses keyed by network symbol
    """
    if not validate_mnemonic(mnemonic):
        logging.warning(f"Invalid mnemonic: {mnemonic}")
        return None
    
    try:
        # Generate seed from mnemonic
        seed = Bip39SeedGenerator(mnemonic).Generate()
        addresses = {}
        
        # Bitcoin (BTC)
        btc_bip44 = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
        btc_acc = btc_bip44.Purpose().Coin().Account(account_idx)
        btc_change = btc_acc.Change(Bip44Changes.CHAIN_EXT)
        btc_addr = btc_change.AddressIndex(address_idx)
        addresses['BTC'] = btc_addr.PublicKey().ToAddress()
        
        # Ethereum (ETH)
        eth_bip44 = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
        eth_acc = eth_bip44.Purpose().Coin().Account(account_idx)
        eth_change = eth_acc.Change(Bip44Changes.CHAIN_EXT)
        eth_addr = eth_change.AddressIndex(address_idx)
        addresses['ETH'] = eth_addr.PublicKey().ToAddress()
        
        # Binance Smart Chain (BSC) - uses same address format as ETH
        addresses['BSC'] = addresses['ETH']
        
        # Tron (TRX)
        try:
            trx_bip44 = Bip44.FromSeed(seed, Bip44Coins.TRON)
            trx_acc = trx_bip44.Purpose().Coin().Account(account_idx)
            trx_change = trx_acc.Change(Bip44Changes.CHAIN_EXT)
            trx_addr = trx_change.AddressIndex(address_idx)
            addresses['TRX'] = trx_addr.PublicKey().ToAddress()
        except Exception as e:
            # Fallback for libraries that might not support TRX
            logging.warning(f"Could not generate TRX address: {str(e)}")
            addresses['TRX'] = eth_addr.PublicKey().ToAddress()  # Use ETH as fallback
        
        return addresses
    except Exception as e:
        logging.error(f"Error generating addresses: {str(e)}")
        return None

def get_private_keys(mnemonic, account_idx=0, address_idx=0):
    """
    Get private keys for different cryptocurrencies from a mnemonic.
    WARNING: Handle with extreme care - only use for wallets you own.
    
    Args:
        mnemonic (str): BIP-39 mnemonic seed phrase
        account_idx (int): Account index (default: 0)
        address_idx (int): Address index (default: 0)
        
    Returns:
        dict: Dictionary of private keys keyed by network symbol
    """
    if not validate_mnemonic(mnemonic):
        logging.warning(f"Invalid mnemonic: {mnemonic}")
        return None
    
    try:
        # Generate seed from mnemonic
        seed = Bip39SeedGenerator(mnemonic).Generate()
        private_keys = {}
        
        # Bitcoin (BTC)
        btc_bip44 = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
        btc_acc = btc_bip44.Purpose().Coin().Account(account_idx)
        btc_change = btc_acc.Change(Bip44Changes.CHAIN_EXT)
        btc_addr = btc_change.AddressIndex(address_idx)
        private_keys['BTC'] = btc_addr.PrivateKey().Raw().ToHex()
        
        # Ethereum (ETH)
        eth_bip44 = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
        eth_acc = eth_bip44.Purpose().Coin().Account(account_idx)
        eth_change = eth_acc.Change(Bip44Changes.CHAIN_EXT)
        eth_addr = eth_change.AddressIndex(address_idx)
        private_keys['ETH'] = eth_addr.PrivateKey().Raw().ToHex()
        
        # Binance Smart Chain (BSC) - uses same private key as ETH
        private_keys['BSC'] = private_keys['ETH']
        
        # Tron (TRX)
        try:
            trx_bip44 = Bip44.FromSeed(seed, Bip44Coins.TRON)
            trx_acc = trx_bip44.Purpose().Coin().Account(account_idx)
            trx_change = trx_acc.Change(Bip44Changes.CHAIN_EXT)
            trx_addr = trx_change.AddressIndex(address_idx)
            private_keys['TRX'] = trx_addr.PrivateKey().Raw().ToHex()
        except Exception as e:
            # Fallback for libraries that might not support TRX
            logging.warning(f"Could not generate TRX private key: {str(e)}")
            private_keys['TRX'] = private_keys['ETH']  # Use ETH as fallback
        
        return private_keys
    except Exception as e:
        logging.error(f"Error generating private keys: {str(e)}")
        return None
