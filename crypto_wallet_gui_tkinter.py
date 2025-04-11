#!/usr/bin/env python3
"""
Cryptocurrency Wallet Brute Force Tool - GUI Version (Tkinter)
This application provides a graphical user interface for generating random BIP-39 seed phrases 
and checking for balances across multiple cryptocurrency networks.
"""

import sys
import os
import time
import threading
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

# Import our existing modules
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

class BruteForceWorker(threading.Thread):
    """Worker thread to perform brute force operations"""
    
    def __init__(self, networks, interval, callback):
        super().__init__(daemon=True)
        self.networks = networks
        self.interval = interval
        self.callback = callback
        self.running = True
        self.paused = False
        self.attempts = 0
        self.found = 0
        self.start_time = time.time()
        
        # Read keywords from the file
        self.keywords = self.read_keywords('keywords.txt')
        
    def read_keywords(self, filename):
        """Read BIP-39 keywords from file"""
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.error(f"Keywords file '{filename}' not found.")
            return []
        except Exception as e:
            logging.error(f"Error reading keywords file: {str(e)}")
            return []
    
    def save_findings(self, mnemonic, addresses, balances):
        """Save found wallets with balances to a file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open("found_wallets.txt", "a") as f:
            f.write(f"=== WALLET FOUND: {timestamp} ===\n")
            f.write(f"Seed phrase: {mnemonic}\n")
            
            for network in addresses.keys():
                if network in balances:
                    f.write(f"{network} Address: {addresses[network]}\n")
                    f.write(f"{network} Balance: {balances[network]}\n")
            
            f.write("\n")
    
    def run(self):
        """Main thread function"""
        if not self.keywords or len(self.keywords) < 12:
            self.callback({
                'error': "Error: Keywords file not found or has less than 12 words"
            })
            return
        
        logging.info(f"Starting brute force process for networks: {', '.join(self.networks)}")
        logging.info(f"Loaded {len(self.keywords)} keywords")
        
        from bip_utils import Bip39MnemonicGenerator
        
        while self.running:
            # Handle pause state
            if self.paused:
                time.sleep(0.1)
                continue
                
            try:
                # Generate a valid BIP-39 mnemonic
                mnemonic = Bip39MnemonicGenerator().FromWordsNumber(words_num=12).ToStr()
                
                self.attempts += 1
                
                # Validate the mnemonic
                if not validate_mnemonic(mnemonic):
                    continue
                
                # Generate addresses from the mnemonic
                addresses = generate_addresses(mnemonic)
                if not addresses:
                    continue
                    
                # Check balances for each network
                balances = {}
                formatted_balances = {}
                
                for network in self.networks:
                    if network in addresses:
                        balances[network] = check_balance(network, addresses[network])
                        formatted_balances[network] = format_balance(network, balances[network])
                        time.sleep(self.interval)  # Avoid rate limiting
                
                # Calculate the rate
                elapsed_time = time.time() - self.start_time
                rate = self.attempts / elapsed_time if elapsed_time > 0 else 0
                
                # Send progress update
                self.callback({
                    'type': 'progress',
                    'attempts': self.attempts,
                    'found': self.found,
                    'rate': rate,
                    'mnemonic': mnemonic,
                    'addresses': addresses,
                    'balances': formatted_balances
                })
                
                # Check if any balance found
                if any(balances.values()):
                    self.found += 1
                    
                    logging.info("\n" + "="*50)
                    logging.info("BALANCE FOUND!")
                    logging.info(f"Seed phrase: {mnemonic}")
                    
                    for net in self.networks:
                        if net in addresses:
                            logging.info(f"{net} Address: {addresses[net]}")
                            logging.info(f"{net} Balance: {balances[net]}")
                    
                    logging.info("="*50)
                    
                    # Save to file
                    self.save_findings(mnemonic, addresses, balances)
                    
                    # Send found wallet notification
                    self.callback({
                        'type': 'found',
                        'mnemonic': mnemonic,
                        'addresses': addresses,
                        'balances': formatted_balances
                    })
                
            except Exception as e:
                logging.error(f"Error processing wallet: {str(e)}")
                continue
    
    def stop(self):
        """Stop the thread"""
        self.running = False
    
    def pause(self):
        """Pause the thread"""
        self.paused = True
    
    def resume(self):
        """Resume the thread"""
        self.paused = False


class WalletBruteForceApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Cryptocurrency Wallet Brute Force Tool")
        self.root.geometry("900x600")
        self.root.minsize(800, 600)
        
        self.brute_force_thread = None
        self.is_running = False
        self.is_paused = False
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create paned window for adjustable sections
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel (controls)
        self.left_panel = ttk.Frame(self.paned_window, width=300)
        self.paned_window.add(self.left_panel, weight=1)
        
        # Create right panel (results)
        self.right_panel = ttk.Frame(self.paned_window, width=600)
        self.paned_window.add(self.right_panel, weight=2)
        
        # Setup UI components
        self.setup_left_panel()
        self.setup_right_panel()
        
        # Setup status bar
        self.status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load history if available
        self.load_found_wallets_history()
        
        # Update progress bar periodically
        self.update_progress_bar()
    
    def setup_left_panel(self):
        """Setup left panel with controls"""
        # Network selection frame
        network_frame = ttk.LabelFrame(self.left_panel, text="Networks to Check")
        network_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create network checkboxes
        self.network_vars = {}
        for network in API_CONFIG.keys():
            var = tk.BooleanVar(value=(network == 'BTC'))  # Default select BTC
            self.network_vars[network] = var
            ttk.Checkbutton(network_frame, text=network, variable=var).pack(anchor=tk.W, padx=10, pady=2)
        
        # Add select all/none buttons
        button_frame = ttk.Frame(network_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Select All", command=self.select_all_networks).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Select None", command=self.select_none_networks).pack(side=tk.LEFT, padx=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(self.left_panel, text="Settings")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Interval setting
        interval_frame = ttk.Frame(settings_frame)
        interval_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(interval_frame, text="API Request Interval (seconds):").pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.DoubleVar(value=0.5)
        interval_spinner = ttk.Spinbox(interval_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.interval_var, width=5)
        interval_spinner.pack(side=tk.LEFT, padx=5)
        
        # Report frequency setting
        report_frame = ttk.Frame(settings_frame)
        report_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(report_frame, text="Report Frequency (attempts):").pack(side=tk.LEFT, padx=5)
        self.report_var = tk.IntVar(value=10)
        report_spinner = ttk.Spinbox(report_frame, from_=1, to=1000, increment=5, textvariable=self.report_var, width=5)
        report_spinner.pack(side=tk.LEFT, padx=5)
        
        # Information frame
        info_frame = ttk.LabelFrame(self.left_panel, text="Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_text = tk.Text(info_frame, height=5, wrap=tk.WORD)
        info_text.pack(fill=tk.X, padx=5, pady=5)
        info_text.insert(tk.END, "This tool generates random BIP-39 seed phrases and checks blockchain balances.\n\n"
                        "Warning: For educational purposes only. Using this tool to attempt to access wallets "
                        "that you do not own is illegal and unethical.")
        info_text.config(state=tk.DISABLED)
        
        # Control buttons
        control_frame = ttk.Frame(self.left_panel)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Brute Force", command=self.start_brute_force)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_brute_force, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
    
    def setup_right_panel(self):
        """Setup right panel with results"""
        # Stats frame
        stats_frame = ttk.LabelFrame(self.right_panel, text="Statistics")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create grid for stats
        stats_inner_frame = ttk.Frame(stats_frame)
        stats_inner_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Attempts
        ttk.Label(stats_inner_frame, text="Attempts:").grid(row=0, column=0, padx=5, pady=2)
        self.attempts_label = ttk.Label(stats_inner_frame, text="0", font=("Arial", 12, "bold"))
        self.attempts_label.grid(row=1, column=0, padx=5, pady=2)
        
        # Found
        ttk.Label(stats_inner_frame, text="Found:").grid(row=0, column=1, padx=5, pady=2)
        self.found_label = ttk.Label(stats_inner_frame, text="0", font=("Arial", 12, "bold"))
        self.found_label.grid(row=1, column=1, padx=5, pady=2)
        
        # Rate
        ttk.Label(stats_inner_frame, text="Rate (att/sec):").grid(row=0, column=2, padx=5, pady=2)
        self.rate_label = ttk.Label(stats_inner_frame, text="0.00", font=("Arial", 12, "bold"))
        self.rate_label.grid(row=1, column=2, padx=5, pady=2)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self.right_panel, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Last generated frame
        seed_frame = ttk.LabelFrame(self.right_panel, text="Last Generated Seed Phrase")
        seed_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.seed_text = scrolledtext.ScrolledText(seed_frame, height=2, wrap=tk.WORD)
        self.seed_text.pack(fill=tk.X, padx=5, pady=5)
        self.seed_text.insert(tk.END, "No seed phrase generated yet")
        self.seed_text.config(state=tk.DISABLED)
        
        # Address table frame
        address_frame = ttk.LabelFrame(self.right_panel, text="Addresses and Balances")
        address_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for addresses
        columns = ("network", "address", "balance")
        self.address_tree = ttk.Treeview(address_frame, columns=columns, show="headings")
        self.address_tree.heading("network", text="Network")
        self.address_tree.heading("address", text="Address")
        self.address_tree.heading("balance", text="Balance")
        
        self.address_tree.column("network", width=80, anchor=tk.CENTER)
        self.address_tree.column("balance", width=150, anchor=tk.CENTER)
        self.address_tree.column("address", width=350)
        
        # Add scrollbar
        address_scrollbar = ttk.Scrollbar(address_frame, orient=tk.VERTICAL, command=self.address_tree.yview)
        self.address_tree.configure(yscrollcommand=address_scrollbar.set)
        
        address_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.address_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Found wallets frame
        found_frame = ttk.LabelFrame(self.right_panel, text="Found Wallets")
        found_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for found wallets
        columns = ("timestamp", "network", "balance")
        self.found_tree = ttk.Treeview(found_frame, columns=columns, show="headings")
        self.found_tree.heading("timestamp", text="Timestamp")
        self.found_tree.heading("network", text="Network")
        self.found_tree.heading("balance", text="Balance")
        
        self.found_tree.column("timestamp", width=150)
        self.found_tree.column("network", width=80, anchor=tk.CENTER)
        self.found_tree.column("balance", width=150, anchor=tk.CENTER)
        
        # Add scrollbar
        found_scrollbar = ttk.Scrollbar(found_frame, orient=tk.VERTICAL, command=self.found_tree.yview)
        self.found_tree.configure(yscrollcommand=found_scrollbar.set)
        
        found_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.found_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def select_all_networks(self):
        """Select all networks"""
        for var in self.network_vars.values():
            var.set(True)
    
    def select_none_networks(self):
        """Deselect all networks"""
        for var in self.network_vars.values():
            var.set(False)
    
    def get_selected_networks(self):
        """Get list of selected networks"""
        return [network for network, var in self.network_vars.items() if var.get()]
    
    def start_brute_force(self):
        """Start the brute force process"""
        if self.is_running:
            return
        
        # Get selected networks
        networks = self.get_selected_networks()
        if not networks:
            messagebox.showwarning("Warning", "Please select at least one network.")
            return
        
        # Get interval
        interval = self.interval_var.get()
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.status_bar.config(text="Running...")
        self.progress_bar.start(50)
        
        # Create and start worker thread
        self.brute_force_thread = BruteForceWorker(
            networks, 
            interval, 
            self.update_ui
        )
        self.brute_force_thread.start()
        
        self.is_running = True
        self.is_paused = False
    
    def toggle_pause(self):
        """Toggle pause/resume state"""
        if not self.is_running or not self.brute_force_thread:
            return
        
        if self.is_paused:
            # Resume
            self.brute_force_thread.resume()
            self.pause_button.config(text="Pause")
            self.status_bar.config(text="Running...")
            self.progress_bar.start(50)
            self.is_paused = False
        else:
            # Pause
            self.brute_force_thread.pause()
            self.pause_button.config(text="Resume")
            self.status_bar.config(text="Paused")
            self.progress_bar.stop()
            self.is_paused = True
    
    def stop_brute_force(self):
        """Stop the brute force process"""
        if not self.is_running or not self.brute_force_thread:
            return
        
        # Stop the thread
        self.brute_force_thread.stop()
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.status_bar.config(text="Stopped")
        self.progress_bar.stop()
        
        self.is_running = False
        self.is_paused = False
        self.pause_button.config(text="Pause")
    
    def update_ui(self, data):
        """Update UI with data from the worker thread"""
        if 'error' in data:
            messagebox.showerror("Error", data['error'])
            self.stop_brute_force()
            return
        
        if data.get('type') == 'progress':
            # Update statistics
            self.attempts_label.config(text=str(data['attempts']))
            self.found_label.config(text=str(data['found']))
            self.rate_label.config(text=f"{data['rate']:.2f}")
            
            # Update seed phrase
            self.seed_text.config(state=tk.NORMAL)
            self.seed_text.delete(1.0, tk.END)
            self.seed_text.insert(tk.END, data['mnemonic'])
            self.seed_text.config(state=tk.DISABLED)
            
            # Update address table
            for item in self.address_tree.get_children():
                self.address_tree.delete(item)
                
            for network, address in data['addresses'].items():
                balance = data['balances'].get(network, "0")
                self.address_tree.insert("", tk.END, values=(network, address, balance))
        
        elif data.get('type') == 'found':
            # Add to found wallets tree
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for network, address in data['addresses'].items():
                if network in data['balances']:
                    self.found_tree.insert("", 0, values=(timestamp, network, data['balances'][network]))
            
            # Show message box
            messagebox.showinfo("Wallet Found!", 
                               f"Found wallet with balance!\nSeed phrase: {data['mnemonic']}")
    
    def update_progress_bar(self):
        """Update progress bar animation"""
        if self.is_running and not self.is_paused:
            self.progress_bar.step(5)
            
        self.root.after(100, self.update_progress_bar)
    
    def load_found_wallets_history(self):
        """Load history of found wallets from the file"""
        try:
            if not os.path.exists('found_wallets.txt'):
                return
                
            with open('found_wallets.txt', 'r') as f:
                content = f.read()
                wallet_blocks = content.split('=== WALLET FOUND:')
                
                for block in wallet_blocks:
                    if block.strip():
                        # Parse wallet details from the block
                        lines = block.strip().split('\n')
                        timestamp = lines[0].strip() if lines else ""
                        
                        addresses = {}
                        balances = {}
                        
                        for line in lines:
                            if 'Address:' in line:
                                parts = line.split('Address:')
                                if len(parts) == 2:
                                    network = parts[0].strip()
                                    address = parts[1].strip()
                                    addresses[network] = address
                            elif 'Balance:' in line:
                                parts = line.split('Balance:')
                                if len(parts) == 2:
                                    network = parts[0].strip()
                                    balance = parts[1].strip()
                                    balances[network] = balance
                        
                        # Add to found wallets tree
                        for network, address in addresses.items():
                            if network in balances:
                                self.found_tree.insert("", tk.END, values=(timestamp, network, balances[network]))
        except Exception as e:
            logging.error(f"Error loading history: {str(e)}")
            messagebox.showerror("Error", f"Error loading wallet history: {str(e)}")


def main():
    """Main function to start the application"""
    root = tk.Tk()
    app = WalletBruteForceApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, app))
    root.mainloop()


def on_closing(root, app):
    """Handle window closing"""
    if app.is_running and app.brute_force_thread:
        if messagebox.askyesno("Confirm Exit", "The brute force process is still running. Are you sure you want to exit?"):
            app.brute_force_thread.stop()
            root.destroy()
    else:
        root.destroy()


if __name__ == "__main__":
    main()