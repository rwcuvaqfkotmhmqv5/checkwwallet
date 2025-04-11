#!/usr/bin/env python3
"""
Cryptocurrency Wallet Brute Force Tool - Simplified Version with i18n Support
This script generates random BIP-39 seed phrases and checks for balances
across multiple blockchain networks.

This version includes support for multiple languages, including English and Vietnamese.
"""

import os
import sys
import time
import random
import logging
import threading
import argparse
import requests
from datetime import datetime
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from bip_utils.bip.bip39.bip39_mnemonic import Bip39MnemonicValidator, Bip39Languages

# Import config with internationalization support
from config_i18n import API_CONFIG, CONVERSION_FACTORS, get_text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("brute_force_log.txt"),
        logging.StreamHandler()
    ]
)

# Global variables
running = True
paused = False
stats = {
    'attempts': 0,
    'found': 0,
    'start_time': time.time()
}

def read_keywords(filename, language='en'):
    """Read BIP-39 keywords from a file."""
    logging.info(get_text('reading_keywords', language))
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def validate_mnemonic(mnemonic):
    """Validate if a mnemonic phrase is valid according to BIP-39 standard."""
    try:
        return Bip39MnemonicValidator(mnemonic).Validate()
    except:
        return False

def generate_addresses(mnemonic):
    """Generate cryptocurrency addresses from a BIP-39 mnemonic."""
    try:
        # Generate seed from mnemonic
        seed = Bip39SeedGenerator(mnemonic).Generate()
        
        # Dictionary to store addresses
        addresses = {}
        
        # BTC address
        btc_wallet = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).DeriveDefaultPath()
        addresses['BTC'] = btc_wallet.PublicKey().ToAddress()
        
        # ETH address (also used for BSC)
        eth_wallet = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM).DeriveDefaultPath()
        eth_address = eth_wallet.PublicKey().ToAddress()
        addresses['ETH'] = eth_address
        addresses['BSC'] = eth_address  # BSC shares the same address format as ETH
        
        # TRX address
        # Note: Real Tron address generation would require a different derivation
        # This is simplified for the example
        addresses['TRX'] = eth_address
        
        return addresses
    except Exception as e:
        logging.debug(f"Address generation error: {str(e)}")
        return None

def check_balance(network, address):
    """Check balance of a wallet address on a specific network."""
    config = API_CONFIG[network]
    try:
        if network == 'BTC':
            response = requests.get(config['url'].format(address=address))
            if response.status_code == 200:
                return response.json()[address]['final_balance']
            return 0
        elif network == 'TRX':
            headers = {'TRON-PRO-API-KEY': config['key']} if config['key'] else {}
            response = requests.get(config['url'].format(address=address), headers=headers)
            if response.status_code == 200:
                # For Tron, the balance is often in the data array
                return int(response.json().get('data', [{}])[0].get('balance', 0))
            return 0
        else:  # ETH, BSC
            url = config['url'].format(
                address=address,
                key=config['key'] if config['key'] else 'YourApiKeyToken'
            )
            response = requests.get(url)
            if response.status_code == 200:
                return int(response.json().get('result', 0))
            return 0
    except Exception as e:
        logging.debug(f"Balance check error ({network}): {str(e)}")
        return 0

def format_balance(network, balance):
    """Format raw balance to human-readable form."""
    if network in CONVERSION_FACTORS and balance > 0:
        formatted = balance / CONVERSION_FACTORS[network]
        return f"{formatted:.8f} {network}"
    return f"0 {network}"

def save_findings(mnemonic, addresses, balances, language='en'):
    """Save found wallets with balances to a file."""
    found_file = "found_wallets.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(found_file, "a", encoding='utf-8') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"{timestamp}\n")
        f.write(f"{get_text('seed_phrase', language)}: {mnemonic}\n\n")
        
        for network in addresses:
            f.write(f"{network}:\n")
            f.write(f"  {get_text('wallet_address', language)}: {addresses[network]}\n")
            f.write(f"  {get_text('balance', language)}: {format_balance(network, balances[network])}\n")
    
    logging.info(f"{get_text('saved_to_file', language)}: {found_file}")
    return found_file

def display_stats(language='en'):
    """Display current statistics."""
    elapsed = time.time() - stats['start_time']
    attempts_per_sec = stats['attempts'] / elapsed if elapsed > 0 else 0
    
    logging.info(f"{get_text('stats', language)}: {stats['attempts']} {get_text('attempts', language)}, "
                 f"{stats['found']} {get_text('found', language)}, "
                 f"{attempts_per_sec:.2f} {get_text('attempts_per_sec', language)}")

def stop_monitor(language='en'):
    """Function to handle stopping the monitoring process."""
    global running
    input(f"\n{get_text('press_enter_to_stop', language)}\n")
    running = False
    logging.info(get_text('stopping_process', language))

def brute_force(keywords, target_networks, language='en', check_interval=1.0, report_interval=100):
    """
    Main brute force function to generate and check wallets.
    
    Args:
        keywords: List of BIP-39 keywords
        target_networks: List of networks to check
        language: Language for output messages
        check_interval: Time to wait between API calls
        report_interval: How often to report statistics
    """
    global running, paused, stats
    
    if len(keywords) < 12:
        logging.error(get_text('require_keywords', language))
        return
    
    logging.info(get_text('starting_process', language))
    
    # Start a thread to monitor for user input to stop
    threading.Thread(target=stop_monitor, args=(language,), daemon=True).start()
    
    current_interval = check_interval
    
    while running:
        if paused:
            time.sleep(0.5)
            continue
        
        # Generate random seed phrase
        selected_words = random.sample(keywords, 12)
        mnemonic = ' '.join(selected_words)
        
        # Validate the mnemonic
        if not validate_mnemonic(mnemonic):
            logging.debug(get_text('invalid_mnemonic', language))
            continue
        
        # Generate addresses for the mnemonic
        addresses = generate_addresses(mnemonic)
        if not addresses:
            continue
        
        # Check balances across target networks
        balances = {}
        has_balance = False
        
        for network in target_networks:
            if network in addresses:
                try:
                    balance = check_balance(network, addresses[network])
                    balances[network] = balance
                    
                    if balance > 0:
                        has_balance = True
                    
                    # Wait between API calls to avoid rate limiting
                    if network != target_networks[-1]:  # Don't wait after the last one
                        time.sleep(current_interval)
                        
                except Exception as e:
                    if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                        logging.warning(get_text('error_api_rate_limit', language))
                        current_interval += 0.5
                    else:
                        logging.warning(f"{get_text('error_connection', language)}: {str(e)}")
                    
                    balances[network] = 0
        
        # Record attempt
        stats['attempts'] += 1
        
        # Report progress at intervals
        if stats['attempts'] % report_interval == 0:
            display_stats(language)
        
        # If a wallet with balance is found
        if has_balance:
            stats['found'] += 1
            logging.info(f"\n{get_text('wallet_found', language)}")
            logging.info(f"{get_text('seed_phrase', language)}: {mnemonic}")
            
            for network in target_networks:
                if network in balances and balances[network] > 0:
                    logging.info(f"{network}: {format_balance(network, balances[network])}")
            
            save_findings(mnemonic, addresses, balances, language)

def main():
    """Main function to start the brute force process."""
    parser = argparse.ArgumentParser(description='Cryptocurrency Wallet Brute Force Tool')
    parser.add_argument('--networks', nargs='+', default=['BTC', 'ETH', 'BSC', 'TRX'],
                       help='Networks to check (default: BTC ETH BSC TRX)')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Interval between API calls in seconds (default: 1.0)')
    parser.add_argument('--report', type=int, default=100,
                       help='Report statistics after this many attempts (default: 100)')
    parser.add_argument('--language', type=str, default='en', choices=['en', 'vi'],
                       help='Language for output messages (default: en)')
    parser.add_argument('--keywords', type=str, default='keywords.txt',
                       help='Path to keywords file (default: keywords.txt)')
    
    args = parser.parse_args()
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    keywords_path = os.path.join(script_dir, args.keywords)
    
    # Check if keywords file exists
    if not os.path.exists(keywords_path):
        logging.error(f"Keywords file not found: {keywords_path}")
        sys.exit(1)
    
    # Read keywords and start brute force process
    keywords = read_keywords(keywords_path, args.language)
    brute_force(
        keywords=keywords,
        target_networks=args.networks,
        language=args.language,
        check_interval=args.interval,
        report_interval=args.report
    )

if __name__ == "__main__":
    main()