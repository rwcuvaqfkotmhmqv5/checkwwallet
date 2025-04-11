#!/usr/bin/env python3
"""
Build script to create a GUI executable with PyInstaller
"""

import os
import platform
import subprocess
import shutil
import sys

def main():
    """Main function to build the executable"""
    print("Building Cryptocurrency Wallet Brute Force Tool executable...")
    
    # Ensure the output directory exists
    os.makedirs("dist_exe", exist_ok=True)
    
    # PyInstaller options
    pyinstaller_options = [
        "crypto_wallet_gui.py",                   # Main script
        "--name=Crypto_Wallet_Brute_Force_GUI",   # Name of the executable
        "--onefile",                              # Package as a single executable
        "--windowed",                             # Don't open console window
        "--add-data=keywords.txt:.",              # Include keywords file
        "--clean",                                # Clean PyInstaller cache
        "--distpath=dist_exe",                    # Output directory
        "--icon=generated-icon.png",              # Application icon
        "--hidden-import=bip_utils",              # Explicitly include bip_utils package
        "--hidden-import=bip_utils.bip.bip39",    # Include specific bip_utils modules
        "--hidden-import=bip_utils.bip.bip44"     # Include specific bip_utils modules
    ]
    
    # Additional options for platform-specific builds
    system = platform.system().lower()
    
    if system == "windows":
        # Windows-specific options
        print("Building for Windows...")
    elif system == "darwin":
        # macOS-specific options
        print("Building for macOS...")
    elif system == "linux":
        # Linux-specific options
        print("Building for Linux...")
    else:
        print(f"Unknown platform: {system}")
    
    # Build the command
    command = ["pyinstaller"] + pyinstaller_options
    
    # Execute PyInstaller
    try:
        print("Running PyInstaller... This might take a while.")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error building executable:")
        print(e.stderr)
        return
    
    # Copy additional files to the distribution directory
    copy_additional_files()
    
    print("Build process completed.")
    print(f"Executable can be found in the '{os.path.abspath('dist_exe')}' directory.")

def copy_additional_files():
    """Copy additional files to the distribution directory"""
    files_to_copy = [
        "README.md",
        "found_wallets.txt",
        "brute_force_log.txt"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            try:
                shutil.copy(file, "dist_exe/")
                print(f"Copied {file} to distribution directory")
            except Exception as e:
                print(f"Error copying {file}: {str(e)}")

if __name__ == "__main__":
    main()