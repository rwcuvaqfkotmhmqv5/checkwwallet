"""
Balance checker module for the cryptocurrency brute force tool.
Handles API calls to various blockchain explorers to check wallet balances.
"""

import time
import logging
import requests
from config import API_CONFIG, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY

def check_balance(network, address):
    """
    Check balance of a wallet address on a specific network.
    
    Args:
        network (str): Network symbol (BTC, ETH, BSC, TRX)
        address (str): Wallet address to check
        
    Returns:
        int: Balance in the smallest unit of the currency (satoshi, wei, etc.)
             Returns 0 if balance check fails.
    """
    if network not in API_CONFIG:
        logging.error(f"Unsupported network: {network}")
        return 0
    
    config = API_CONFIG[network]
    
    # Retry logic for API calls
    for attempt in range(MAX_RETRIES):
        try:
            if attempt > 0:
                logging.info(f"Retry {attempt}/{MAX_RETRIES} for {network} address {address}")
                time.sleep(RETRY_DELAY)
            
            if network == 'BTC':
                return _check_btc_balance(address, config)
            elif network == 'ETH':
                return _check_eth_balance(address, config)
            elif network == 'BSC':
                return _check_bsc_balance(address, config)
            elif network == 'TRX':
                return _check_trx_balance(address, config)
            else:
                logging.warning(f"No implementation for {network} balance check")
                return 0
        
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request error checking {network} balance for {address}: {str(e)}")
            continue
        except Exception as e:
            logging.error(f"Error checking {network} balance for {address}: {str(e)}")
            break
    
    return 0

def _check_btc_balance(address, config):
    """Check Bitcoin balance."""
    url = config['url'].format(address=address)
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    
    if response.status_code == 200:
        data = response.json()
        if address in data:
            return data[address].get('final_balance', 0)
    
    return 0

def _check_eth_balance(address, config):
    """Check Ethereum balance."""
    url = config['url'].format(address=address, api_key=config['key'] or '')
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == '1':
            return int(data.get('result', 0))
    
    return 0

def _check_bsc_balance(address, config):
    """Check Binance Smart Chain balance."""
    url = config['url'].format(address=address, api_key=config['key'] or '')
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == '1':
            return int(data.get('result', 0))
    
    return 0

def _check_trx_balance(address, config):
    """Check Tron balance."""
    url = config['url'].format(address=address)
    headers = {}
    if config['key']:
        headers['TRON-PRO-API-KEY'] = config['key']
    
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    
    if response.status_code == 200:
        data = response.json()
        account_data = data.get('data', [{}])[0]
        return int(account_data.get('balance', 0))
    
    return 0

def format_balance(network, balance):
    """
    Format raw balance to human-readable form.
    
    Args:
        network (str): Network symbol
        balance (int): Raw balance
        
    Returns:
        str: Formatted balance with currency symbol
    """
    if network == 'BTC':
        # 1 BTC = 100,000,000 satoshis
        return f"{balance / 100000000:.8f} BTC"
    elif network == 'ETH':
        # 1 ETH = 10^18 wei
        return f"{balance / 1000000000000000000:.18f} ETH"
    elif network == 'BSC':
        # 1 BNB = 10^18 wei
        return f"{balance / 1000000000000000000:.18f} BNB"
    elif network == 'TRX':
        # 1 TRX = 1,000,000 sun
        return f"{balance / 1000000:.6f} TRX"
    else:
        return f"{balance} (raw units)"
