from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import json
import threading
import time
import logging
from datetime import datetime

from wallet_generator import generate_addresses, validate_mnemonic
from balance_checker import check_balance, format_balance
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

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Global variables for the brute force process
brute_force_thread = None
running = False
attempts = 0
found_wallets = 0
last_generated = None
last_addresses = None
last_balances = None
selected_networks = []  # Track currently selected networks
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

def get_status():
    """Get current status of the brute force process."""
    global attempts, found_wallets, last_generated, last_addresses, last_balances, stats, selected_networks
    
    if stats["start_time"] is not None:
        elapsed_time = time.time() - stats["start_time"]
        rate = attempts / elapsed_time if elapsed_time > 0 else 0
        stats["rate"] = rate
    
    formatted_balances = {}
    if last_balances:
        for network, balance in last_balances.items():
            formatted_balances[network] = format_balance(network, balance)
    
    return {
        "running": running,
        "attempts": attempts,
        "found": found_wallets,
        "rate": stats["rate"],
        "last_mnemonic": last_generated,
        "last_addresses": last_addresses,
        "last_balances": formatted_balances,
        "selected_networks": selected_networks  # Return selected networks to the UI
    }

def brute_force_process(keywords, target_networks, check_interval=1.0):
    """Main brute force function to generate and check wallets."""
    global running, attempts, found_wallets, last_generated, last_addresses, last_balances, stats, selected_networks
    
    import random
    from bip_utils import Bip39MnemonicGenerator, Bip39Languages
    
    stats["start_time"] = time.time()
    
    logging.info(f"Starting brute force process for networks: {', '.join(target_networks)}")
    logging.info(f"Loaded {len(keywords)} keywords")
    
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
                        logging.info(f"{net} Balance: {balances[net]}")
                
                logging.info("="*50)
                
                # Save to file
                save_findings(mnemonic, addresses, balances)
            
            # Update stats periodically
            if attempts % 10 == 0:
                elapsed_time = time.time() - stats["start_time"]
                rate = attempts / elapsed_time if elapsed_time > 0 else 0
                stats["rate"] = rate
        
        except Exception as e:
            logging.error(f"Error processing wallet: {str(e)}")
            continue

@app.route('/')
def index():
    """Main page route."""
    keywords_count = 0
    try:
        with open('keywords.txt', 'r') as f:
            keywords_count = sum(1 for line in f if line.strip())
    except:
        pass
    
    networks = list(API_CONFIG.keys())
    return render_template(
        'index.html', 
        status=get_status(), 
        networks=networks,
        keywords_count=keywords_count
    )

@app.route('/start', methods=['POST'])
def start():
    """Start the brute force process."""
    global brute_force_thread, running, attempts, found_wallets, last_generated, last_addresses, last_balances, stats, selected_networks
    
    if running:
        flash('Brute force process is already running.', 'warning')
        return redirect(url_for('index'))
    
    # Get parameters from form
    networks = request.form.getlist('networks')
    interval = float(request.form.get('interval', 1.0))
    
    # Validate networks
    valid_networks = [n for n in networks if n in API_CONFIG]
    
    if not valid_networks:
        flash('No valid networks selected.', 'danger')
        return redirect(url_for('index'))
    
    # Read keywords
    keywords = read_keywords('keywords.txt')
    if not keywords:
        flash('Failed to read keywords file.', 'danger')
        return redirect(url_for('index'))
    
    # Reset stats
    running = True
    attempts = 0
    found_wallets = 0
    last_generated = None
    last_addresses = None
    last_balances = None
    selected_networks = valid_networks  # Store the selected networks
    stats = {
        "start_time": None,
        "attempts": 0,
        "found": 0,
        "rate": 0
    }
    
    # Start the brute force process in a thread
    brute_force_thread = threading.Thread(
        target=brute_force_process,
        args=(keywords, valid_networks, interval),
        daemon=True
    )
    brute_force_thread.start()
    
    flash('Brute force process started.', 'success')
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    """Stop the brute force process."""
    global running
    
    if running:
        running = False
        flash('Brute force process stopped.', 'info')
    else:
        flash('No brute force process is running.', 'warning')
    
    return redirect(url_for('index'))

@app.route('/status')
def status():
    """API endpoint to get current status."""
    return jsonify(get_status())

@app.route('/history')
def history():
    """View found wallets history."""
    found_wallets = []
    try:
        with open('found_wallets.txt', 'r') as f:
            content = f.read()
            wallet_blocks = content.split('=== WALLET FOUND:')
            
            for block in wallet_blocks:
                if block.strip():
                    # Parse wallet details from the block
                    lines = block.strip().split('\n')
                    timestamp = lines[0].strip() if lines else ""
                    
                    wallet = {
                        'timestamp': timestamp,
                        'mnemonic': '',
                        'addresses': {},
                        'balances': {}
                    }
                    
                    for line in lines[1:]:
                        if line.startswith('Seed phrase:'):
                            wallet['mnemonic'] = line.replace('Seed phrase:', '').strip()
                        elif 'Address:' in line:
                            parts = line.split('Address:')
                            if len(parts) == 2:
                                network = parts[0].strip()
                                address = parts[1].strip()
                                wallet['addresses'][network] = address
                        elif 'Balance:' in line:
                            parts = line.split('Balance:')
                            if len(parts) == 2:
                                network = parts[0].strip()
                                balance = parts[1].strip()
                                wallet['balances'][network] = balance
                    
                    found_wallets.append(wallet)
    except Exception as e:
        flash(f'Error reading history: {str(e)}', 'danger')
    
    return render_template('history.html', wallets=found_wallets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)