#!/usr/bin/env python3
"""
Cryptocurrency Wallet Brute Force Tool - GUI Version
This application provides a graphical user interface for generating random BIP-39 seed phrases 
and checking for balances across multiple cryptocurrency networks.
"""

import sys
import os
import time
import threading
import logging
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QCheckBox, QDoubleSpinBox, QTableWidget, 
    QTableWidgetItem, QTextEdit, QGroupBox, QProgressBar, QMessageBox,
    QHeaderView, QSpinBox, QSplitter, QStatusBar, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIcon

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
    
    def __init__(self, networks, interval, progress_callback, seed_callback):
        super().__init__(daemon=True)
        self.networks = networks
        self.interval = interval
        self.progress_callback = progress_callback
        self.seed_callback = seed_callback
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
            self.progress_callback.emit({
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
                self.progress_callback.emit({
                    'attempts': self.attempts,
                    'found': self.found,
                    'rate': rate
                })
                
                # Send seed update
                self.seed_callback.emit({
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
                    
                    # Send progress update with found wallet
                    self.progress_callback.emit({
                        'attempts': self.attempts,
                        'found': self.found,
                        'rate': rate,
                        'found_wallet': {
                            'mnemonic': mnemonic,
                            'addresses': addresses,
                            'balances': formatted_balances
                        }
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


class MainWindow(QMainWindow):
    """Main application window"""
    
    # Define custom signals
    progress_signal = pyqtSignal(dict)
    seed_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.brute_force_thread = None
        self.is_running = False
        self.is_paused = False
        
        self.setWindowTitle("Cryptocurrency Wallet Brute Force Tool")
        self.setMinimumSize(900, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for flexible layout
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create left panel (controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        splitter.addWidget(left_panel)
        
        # Create right panel (results)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        splitter.addWidget(right_panel)
        
        # Set the initial sizes of the splitter
        splitter.setSizes([300, 600])
        
        # Create network selection group
        network_group = QGroupBox("Networks to Check")
        network_layout = QVBoxLayout(network_group)
        
        # Add network checkboxes
        self.network_checkboxes = {}
        for network in API_CONFIG.keys():
            checkbox = QCheckBox(network)
            if network == 'BTC':  # Default select BTC
                checkbox.setChecked(True)
            self.network_checkboxes[network] = checkbox
            network_layout.addWidget(checkbox)
        
        # Add select all/none buttons
        select_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_none_btn = QPushButton("Select None")
        select_all_btn.clicked.connect(self.select_all_networks)
        select_none_btn.clicked.connect(self.select_none_networks)
        select_layout.addWidget(select_all_btn)
        select_layout.addWidget(select_none_btn)
        network_layout.addLayout(select_layout)
        
        left_layout.addWidget(network_group)
        
        # Create interval selection
        interval_group = QGroupBox("Settings")
        interval_layout = QVBoxLayout(interval_group)
        
        interval_h_layout = QHBoxLayout()
        interval_label = QLabel("API Request Interval (seconds):")
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 10.0)
        self.interval_spin.setSingleStep(0.1)
        self.interval_spin.setValue(0.5)
        interval_h_layout.addWidget(interval_label)
        interval_h_layout.addWidget(self.interval_spin)
        interval_layout.addLayout(interval_h_layout)
        
        report_h_layout = QHBoxLayout()
        report_label = QLabel("Report Frequency (attempts):")
        self.report_spin = QSpinBox()
        self.report_spin.setRange(1, 1000)
        self.report_spin.setSingleStep(5)
        self.report_spin.setValue(10)
        report_h_layout.addWidget(report_label)
        report_h_layout.addWidget(self.report_spin)
        interval_layout.addLayout(report_h_layout)
        
        left_layout.addWidget(interval_group)
        
        # Information group
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel("This tool generates random BIP-39 seed phrases and checks blockchain balances.\n\n"
                          "Warning: For educational purposes only. Using this tool to attempt to access wallets "
                          "that you do not own is illegal and unethical.")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        left_layout.addWidget(info_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Brute Force")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        
        self.start_button.clicked.connect(self.start_brute_force)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.stop_button.clicked.connect(self.stop_brute_force)
        
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        
        left_layout.addLayout(button_layout)
        
        # Add a spacer to the bottom of the left panel
        left_layout.addStretch()
        
        # Right panel - Stats and results
        # Stats group
        stats_group = QGroupBox("Statistics")
        stats_layout = QHBoxLayout(stats_group)
        
        # Attempts
        attempts_layout = QVBoxLayout()
        attempts_label = QLabel("Attempts:")
        self.attempts_value = QLabel("0")
        self.attempts_value.setAlignment(Qt.AlignCenter)
        self.attempts_value.setFont(QFont('Arial', 16, QFont.Bold))
        attempts_layout.addWidget(attempts_label)
        attempts_layout.addWidget(self.attempts_value)
        stats_layout.addLayout(attempts_layout)
        
        # Found
        found_layout = QVBoxLayout()
        found_label = QLabel("Found:")
        self.found_value = QLabel("0")
        self.found_value.setAlignment(Qt.AlignCenter)
        self.found_value.setFont(QFont('Arial', 16, QFont.Bold))
        found_layout.addWidget(found_label)
        found_layout.addWidget(self.found_value)
        stats_layout.addLayout(found_layout)
        
        # Rate
        rate_layout = QVBoxLayout()
        rate_label = QLabel("Rate (att/sec):")
        self.rate_value = QLabel("0.00")
        self.rate_value.setAlignment(Qt.AlignCenter)
        self.rate_value.setFont(QFont('Arial', 16, QFont.Bold))
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(self.rate_value)
        stats_layout.addLayout(rate_layout)
        
        right_layout.addWidget(stats_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        right_layout.addWidget(self.progress_bar)
        
        # Last generated label
        self.last_generated_label = QLabel("Last Generated Seed Phrase:")
        right_layout.addWidget(self.last_generated_label)
        
        # Seed phrase text box
        self.seed_phrase_text = QTextEdit()
        self.seed_phrase_text.setReadOnly(True)
        self.seed_phrase_text.setMaximumHeight(60)
        self.seed_phrase_text.setPlaceholderText("No seed phrase generated yet")
        right_layout.addWidget(self.seed_phrase_text)
        
        # Address and balance table
        self.address_table = QTableWidget(0, 3)
        self.address_table.setHorizontalHeaderLabels(["Network", "Address", "Balance"])
        self.address_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.address_table.verticalHeader().setVisible(False)
        right_layout.addWidget(self.address_table)
        
        # Found wallets table
        found_wallets_label = QLabel("Found Wallets:")
        right_layout.addWidget(found_wallets_label)
        
        self.found_table = QTableWidget(0, 3)
        self.found_table.setHorizontalHeaderLabels(["Timestamp", "Network", "Balance"])
        self.found_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.found_table.verticalHeader().setVisible(False)
        right_layout.addWidget(self.found_table)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Connect signals
        self.progress_signal.connect(self.update_progress)
        self.seed_signal.connect(self.update_seed)
        
        # Setup update timer for progress bar animation
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_bar)
        self.progress_timer.start(100)
        
        # Load history if available
        self.load_found_wallets_history()
    
    def select_all_networks(self):
        """Select all networks"""
        for checkbox in self.network_checkboxes.values():
            checkbox.setChecked(True)
    
    def select_none_networks(self):
        """Deselect all networks"""
        for checkbox in self.network_checkboxes.values():
            checkbox.setChecked(False)
    
    def get_selected_networks(self):
        """Get list of selected networks"""
        return [network for network, checkbox in self.network_checkboxes.items() 
                if checkbox.isChecked()]
    
    def start_brute_force(self):
        """Start the brute force process"""
        if self.is_running:
            return
        
        # Get selected networks
        networks = self.get_selected_networks()
        if not networks:
            QMessageBox.warning(self, "Warning", "Please select at least one network.")
            return
        
        # Get interval
        interval = self.interval_spin.value()
        
        # Update UI
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.status_bar.showMessage("Running...")
        
        # Create and start worker thread
        self.brute_force_thread = BruteForceWorker(
            networks, 
            interval, 
            self.progress_signal,
            self.seed_signal
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
            self.pause_button.setText("Pause")
            self.status_bar.showMessage("Running...")
            self.is_paused = False
        else:
            # Pause
            self.brute_force_thread.pause()
            self.pause_button.setText("Resume")
            self.status_bar.showMessage("Paused")
            self.is_paused = True
    
    def stop_brute_force(self):
        """Stop the brute force process"""
        if not self.is_running or not self.brute_force_thread:
            return
        
        # Stop the thread
        self.brute_force_thread.stop()
        
        # Update UI
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.status_bar.showMessage("Stopped")
        
        self.is_running = False
        self.is_paused = False
        self.pause_button.setText("Pause")
    
    @pyqtSlot(dict)
    def update_progress(self, progress_data):
        """Update progress information"""
        if 'error' in progress_data:
            QMessageBox.critical(self, "Error", progress_data['error'])
            self.stop_brute_force()
            return
        
        # Update statistics
        if 'attempts' in progress_data:
            self.attempts_value.setText(str(progress_data['attempts']))
        
        if 'found' in progress_data:
            self.found_value.setText(str(progress_data['found']))
        
        if 'rate' in progress_data:
            self.rate_value.setText(f"{progress_data['rate']:.2f}")
        
        # Handle found wallet
        if 'found_wallet' in progress_data:
            self.add_found_wallet(progress_data['found_wallet'])
    
    @pyqtSlot(dict)
    def update_seed(self, seed_data):
        """Update seed phrase and address information"""
        if 'mnemonic' in seed_data:
            self.seed_phrase_text.setText(seed_data['mnemonic'])
        
        if 'addresses' in seed_data and 'balances' in seed_data:
            # Clear the table
            self.address_table.setRowCount(0)
            
            # Add rows
            for network, address in seed_data['addresses'].items():
                row = self.address_table.rowCount()
                self.address_table.insertRow(row)
                
                # Network
                self.address_table.setItem(row, 0, QTableWidgetItem(network))
                
                # Address
                self.address_table.setItem(row, 1, QTableWidgetItem(address))
                
                # Balance
                balance = seed_data['balances'].get(network, "0")
                self.address_table.setItem(row, 2, QTableWidgetItem(balance))
    
    def update_progress_bar(self):
        """Update progress bar animation"""
        if self.is_running and not self.is_paused:
            current_value = self.progress_bar.value()
            next_value = (current_value + 5) % 100
            self.progress_bar.setValue(next_value)
    
    def add_found_wallet(self, wallet_data):
        """Add a found wallet to the table"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add to found wallets table
        for network, address in wallet_data['addresses'].items():
            if network in wallet_data['balances']:
                row = self.found_table.rowCount()
                self.found_table.insertRow(row)
                
                # Timestamp
                self.found_table.setItem(row, 0, QTableWidgetItem(timestamp))
                
                # Network
                self.found_table.setItem(row, 1, QTableWidgetItem(network))
                
                # Balance
                self.found_table.setItem(row, 2, QTableWidgetItem(wallet_data['balances'][network]))
        
        # Show message box
        QMessageBox.information(self, "Wallet Found!", 
                               f"Found wallet with balance!\nSeed phrase: {wallet_data['mnemonic']}")
    
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
                        
                        # Add to found wallets table
                        for network, address in addresses.items():
                            if network in balances:
                                row = self.found_table.rowCount()
                                self.found_table.insertRow(row)
                                
                                # Timestamp
                                self.found_table.setItem(row, 0, QTableWidgetItem(timestamp))
                                
                                # Network
                                self.found_table.setItem(row, 1, QTableWidgetItem(network))
                                
                                # Balance
                                self.found_table.setItem(row, 2, QTableWidgetItem(balances[network]))
        except Exception as e:
            logging.error(f"Error loading history: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_running and self.brute_force_thread:
            # Ask for confirmation
            reply = QMessageBox.question(
                self, "Confirm Exit",
                "The brute force process is still running. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.brute_force_thread.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main function to start the application"""
    app = QApplication(sys.argv)
    
    # Set style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()