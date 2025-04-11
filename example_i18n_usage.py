"""
Example demonstrating how to use the internationalization features
of the cryptocurrency wallet brute force tool.
"""

import argparse
import time
from config_i18n import get_text, TRANSLATIONS

def main():
    """
    Main function demonstrating internationalization features
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Cryptocurrency Wallet Brute Force Tool")
    parser.add_argument('--language', type=str, default='en',
                        choices=TRANSLATIONS.keys(),
                        help="Language for output messages (en, vi)")
    args = parser.parse_args()
    
    language = args.language
    
    # Display welcome header
    print("\n" + "="*50)
    print("CRYPTOCURRENCY WALLET BRUTE FORCE TOOL - I18N DEMO")
    print("="*50 + "\n")
    
    # Display startup message
    print(get_text('reading_keywords', language))
    print(get_text('starting_process', language))
    print()
    
    # Display available networks
    print("Available Networks:")
    networks = ["Bitcoin (BTC)", "Ethereum (ETH)", 
                "Binance Smart Chain (BSC)", "Tron (TRX)"]
    for i, network in enumerate(networks, 1):
        print(f"  {i}. {network}")
    print()
    
    # Create a simulated wallet
    seed_phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    addresses = {
        "BTC": "1PnMfRF2enSZnR6iiCCRHb7rLGX5Zbu9L2",
        "ETH": "0x83fD2C73B7b6f757B9C4664Fe3F84241c23D9B82",
        "BSC": "0x83fD2C73B7b6f757B9C4664Fe3F84241c23D9B82",
        "TRX": "TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL"
    }
    
    # Display seed phrase info
    print(get_text('seed_phrase', language) + ":", seed_phrase)
    for net, addr in addresses.items():
        print(get_text('wallet_address', language) + f" ({net}):", addr)
    print()
    
    # Demonstrate progress reporting
    print(get_text('stats', language) + ":")
    for i in range(5):
        print(f"{get_text('attempts', language)}: {i+1}, " +
              f"{get_text('found', language)}: 0, " +
              f"{get_text('speed', language)}: 1.2 {get_text('attempts_per_sec', language)}")
        time.sleep(1)
    
    # Display stop message
    print("\n" + get_text('press_enter_to_stop', language))

if __name__ == '__main__':
    main()