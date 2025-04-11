#!/usr/bin/env python3
"""
Build script to create a Tkinter GUI executable with PyInstaller
"""

import os
import sys
import shutil
import platform
import subprocess

def main():
    """Main function to build the executable"""
    print("Building Tkinter GUI executable...")
    
    # Create output directory
    os.makedirs("dist_exe", exist_ok=True)
    
    # Build command for PyInstaller
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=Crypto_Wallet_Brute_Force_GUI_Tkinter",
        "--onefile",
        "--windowed",
        "--add-data=keywords.txt:.",
        "--icon=generated-icon.png",
        "--hidden-import=bip_utils",
        "--hidden-import=bip_utils.bip.bip39",
        "--hidden-import=bip_utils.bip.bip44",
        "crypto_wallet_gui_tkinter.py"
    ]
    
    # Run PyInstaller
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("PyInstaller executed successfully")
        
        # Copy additional files
        copy_additional_files()
        
        print("\nBuild completed successfully!")
        print("Executable is available in the 'dist' directory")
        print(f"Path: {os.path.abspath('dist/Crypto_Wallet_Brute_Force_GUI_Tkinter' + ('.exe' if platform.system() == 'Windows' else ''))}")
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: PyInstaller failed with error code {e.returncode}")
        print("Please make sure PyInstaller is installed:")
        print("  pip install pyinstaller")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Build failed: {str(e)}")
        sys.exit(1)

def copy_additional_files():
    """Copy additional files to the distribution directory"""
    # Files to copy alongside the executable
    files_to_copy = [
        "keywords.txt",
        "README.md",
        "config.py"
    ]
    
    print("\nCopying additional files to distribution directory...")
    for file in files_to_copy:
        if os.path.exists(file):
            try:
                shutil.copy(file, "dist/")
                print(f"  Copied {file}")
            except Exception as e:
                print(f"  Error copying {file}: {str(e)}")

if __name__ == "__main__":
    main()