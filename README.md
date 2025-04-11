# Cryptocurrency Wallet Brute Force Tool

A Python-based cryptocurrency wallet brute-force tool that generates random seed phrases and checks balances across multiple blockchains.

## Features

- Generate valid BIP-39 seed phrases
- Check balances on multiple networks simultaneously:
  - Bitcoin (BTC)
  - Ethereum (ETH)
  - Binance Smart Chain (BSC)
  - Tron (TRX)
- Save found wallets with balances to a file
- Configurable API requests to avoid rate limiting
- Multiple interface options:
  - Command-line interface with customizable options
  - PyQt5-based graphical user interface
  - Tkinter-based graphical user interface (works with standard Python)
- Internationalization support:
  - English
  - Vietnamese (Tiếng Việt)

## Requirements

The tool is available in multiple formats:
1. As a standalone executable for Windows, macOS, and Linux (no installation required)
2. As a ZIP package with Python source code (requires Python and dependencies)

Required Python packages:
- bip-utils (Version 2.9.0 or higher)
- requests
- PyQt5 (only for PyQt5 GUI version)

To install all dependencies at once, run:
```
pip install -r requirements.txt
```

### Known Issue: Missing bip_utils Module

When running the executable version, you may encounter an error: `ModuleNotFoundError: No module named 'bip_utils'`

Solutions:
1. **Run from Python source directly** (recommended)
2. **Rebuild the executable** using the included build scripts which now include explicit imports
3. See the INSTALLATION_GUIDE.txt file for detailed troubleshooting steps

## Usage

### Desktop GUI Applications

#### PyQt5 GUI Version (Advanced Interface)
1. Download and extract the ZIP package
2. Install the required dependencies
3. Run using the provided scripts:
   - On Windows: Double-click `run_gui.bat`
   - On macOS/Linux: Run `chmod +x run_gui.sh` and then `./run_gui.sh`
   
   Or directly: `python crypto_wallet_gui.py`

#### Tkinter GUI Version (Standard Python)
1. Download and extract the ZIP package
2. Install the required dependencies
3. Run using the provided scripts:
   - On Windows: Double-click `run_tkinter_gui.bat`
   - On macOS/Linux: Run `chmod +x run_tkinter_gui.sh` and then `./run_tkinter_gui.sh`
   
   Or directly: `python crypto_wallet_gui_tkinter.py`

### Web Interface
1. Download and extract the ZIP package
2. Install the required dependencies
3. Run the Flask application:
   ```
   python main.py
   ```
4. Open your browser and navigate to `http://localhost:5000`

### Command Line Interface

The tool supports the following command-line options:

```
--networks: Networks to check (e.g., BTC ETH BSC TRX)
--interval: Time to wait between API calls (default: 0.5 seconds)
--report: How often to report statistics (default: 10 attempts)
```

Example:
```
python brute_force_wallet.py --networks BTC ETH --interval 1.0 --report 20
```

## Understanding the Process

This tool generates random BIP-39 seed phrases which are used to create cryptocurrency wallet addresses. It then checks various blockchain networks to see if these addresses contain any funds.

Some important notes:
1. The probability of finding a wallet with a balance is extremely low
2. This is for educational purposes only
3. The tool helps understand blockchain wallet generation and BIP standards

## For Developers

If you want to modify or build the tool from source:

1. Install Python 3.6 or higher
2. Install required packages
3. Run the CLI tool: `python brute_force_wallet.py`
4. Run the PyQt5 GUI: `python crypto_wallet_gui.py`
5. Run the Tkinter GUI: `python crypto_wallet_gui_tkinter.py`
6. To build executables:
   - PyQt5 GUI: `python build_gui_exe.py`
   - Tkinter GUI: `python build_tkinter_gui_exe.py`

## Disclaimer

This tool is for educational purposes only. Using it to attempt to gain unauthorized access to cryptocurrency wallets would be illegal and unethical. The probability of randomly generating a seed phrase that corresponds to a wallet with funds is astronomically low.
