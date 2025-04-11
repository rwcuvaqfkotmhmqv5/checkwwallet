"""
Configuration file for the cryptocurrency wallet brute force tool.
Contains API endpoints and other settings.
"""

import os

# API configuration for different networks
API_CONFIG = {
    'BTC': {
        'url': 'https://blockchain.info/balance?active={address}',
        'key': None
    },
    'ETH': {
        'url': 'https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}',
        'key': os.getenv('ETHERSCAN_API_KEY', '')
    },
    'BSC': {
        'url': 'https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}',
        'key': os.getenv('BSCSCAN_API_KEY', '')
    },
    'TRX': {
        'url': 'https://api.trongrid.io/v1/accounts/{address}',
        'key': os.getenv('TRONGRID_API_KEY', '')
    }
}

# Balance thresholds (in the smallest unit) that are considered significant
BALANCE_THRESHOLDS = {
    'BTC': 1000,  # 1000 satoshis
    'ETH': 10**15,  # 0.001 ETH
    'BSC': 10**15,  # 0.001 BNB
    'TRX': 1000  # 1000 sun
}

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Maximum retries for API calls
MAX_RETRIES = 3

# Delay between retries (in seconds)
RETRY_DELAY = 2
