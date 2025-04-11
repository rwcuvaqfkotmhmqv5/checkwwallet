# Cryptocurrency Wallet Brute Force Tool - User Guide

## Overview

This tool allows you to generate random BIP-39 seed phrases and check if they correspond to cryptocurrency wallets with balances. It supports multiple cryptocurrency networks including Bitcoin (BTC), Ethereum (ETH), Binance Smart Chain (BSC), and Tron (TRX).

## Getting Started

### System Requirements

- Windows, macOS, or Linux operating system
- Python 3.6 or higher
- Internet connection for balance checking

### Installation Options

#### Option 1: Run Directly from Python (Recommended)

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Extract the ZIP package to a folder
3. Open a command prompt/terminal in that folder
4. Install required packages:
   ```
   pip install -r requirements.txt
   ```
   
   Make sure the `bip-utils` package is installed properly:
   ```
   pip install bip-utils
   ```

5. Run one of the GUI applications (see below)

#### Option 2: Build a Standalone Executable

1. Follow steps 1-4 from Option 1
2. Make sure you have all dependencies installed:
   ```
   pip install pyinstaller bip-utils
   ```
3. Build the executable:
   - For PyQt5 GUI: `python build_gui_exe.py`
   - For Tkinter GUI: `python build_tkinter_gui_exe.py`
4. Run the executable from the `dist` folder

#### Troubleshooting Missing Modules

If you encounter a `ModuleNotFoundError` for `bip_utils` when running the executable:

1. Make sure the package is installed in your Python environment:
   ```
   pip install bip-utils
   ```
2. Try rebuilding the executable with the updated build scripts which explicitly include the required modules
3. If issues persist, run the Python script directly instead of using the executable

## User Interface Options

This package includes two different graphical user interfaces:

### PyQt5 GUI (Advanced Interface)

This interface provides a modern, feature-rich experience with better styling.

**To run:**
- On Windows: Double-click `run_gui.bat`
- On macOS/Linux: 
  ```
  chmod +x run_gui.sh
  ./run_gui.sh
  ```
- Or directly: `python crypto_wallet_gui.py`

**Requirements:** PyQt5 (included in requirements.txt)

### Tkinter GUI (Compatible Interface)

This interface works with standard Python installations without additional UI libraries.

**To run:**
- On Windows: Double-click `run_tkinter_gui.bat`
- On macOS/Linux:
  ```
  chmod +x run_tkinter_gui.sh
  ./run_tkinter_gui.sh
  ```
- Or directly: `python crypto_wallet_gui_tkinter.py`

**Requirements:** None beyond standard Python

### Simplified Version with Internationalization

A command-line interface with multi-language support.

**To run:**
- For English (default): `python simple_wallet_brute_force.py`
- For Vietnamese: 
  - On Windows: Double-click `run_vietnamese.bat`
  - On macOS/Linux:
    ```
    chmod +x run_vietnamese.sh
    ./run_vietnamese.sh
    ```
- Or with language parameter: `python simple_wallet_brute_force.py --language vi`

**Requirements:** None beyond standard Python


### Web Interface

A browser-based interface is also available:

**To run:**
```
python main.py
```
Then open your browser and navigate to `http://localhost:5000`

## Features

- **Network Selection**: Choose which cryptocurrency networks to check
- **Request Interval**: Configure timing between API calls to avoid rate limiting
- **Progress Tracking**: Real-time statistics on attempts, rate, and found wallets
- **Address Display**: View generated addresses for each network
- **Found Wallet History**: Keep track of any wallets with balances
- **Internationalization**: Support for multiple languages
  - English (default)
  - Vietnamese (Tiếng Việt)
- **Internationalization**: Support for multiple languages
  - English (default)
  - Vietnamese (Tiếng Việt)

## Usage Tips

1. **Start Small**: Begin with just one network (e.g., BTC) to test
2. **Adjust Interval**: If you get API rate limit errors, increase the interval
3. **Be Patient**: The tool works best when left running for extended periods
4. **Resource Usage**: Adjust settings based on your computer's capabilities

## Disclaimer

This tool is for educational purposes only. Using it to attempt to gain unauthorized access to cryptocurrency wallets would be illegal and unethical. The probability of randomly generating a seed phrase that corresponds to a wallet with funds is astronomically low.