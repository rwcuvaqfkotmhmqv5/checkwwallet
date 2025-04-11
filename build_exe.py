"""
Build script to create executable with PyInstaller
"""
import os
import platform
import subprocess
import shutil

def main():
    print("Building cryptocurrency wallet brute force tool executable...")
    
    # Determine the operating system
    os_name = platform.system()
    print(f"Detected OS: {os_name}")
    
    # Clean up any previous build
    for dir_to_clean in ['build', 'dist']:
        if os.path.exists(dir_to_clean):
            print(f"Cleaning up {dir_to_clean} directory...")
            shutil.rmtree(dir_to_clean)
    
    # Set PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--name', 'Crypto_Wallet_Brute_Force',
        '--clean',
        '--icon=generated-icon.png',
        'standalone_wallet_brute_force.py'
    ]
    
    # Add OS-specific options
    if os_name == 'Windows':
        cmd.append('--noconsole')  # No console window on Windows
    
    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)
    
    # Copy required files
    print("Copying required files...")
    dist_dir = 'dist'
    
    # List of files to include with the executable
    files_to_copy = ['keywords.txt', 'README.md']
    
    for file in files_to_copy:
        if os.path.exists(file):
            dest = os.path.join(dist_dir, file)
            print(f"Copying {file} to {dest}")
            shutil.copy2(file, dest)
    
    # Create an empty found_wallets.txt file
    with open(os.path.join(dist_dir, 'found_wallets.txt'), 'w') as f:
        f.write("# Found wallets will be saved here\n")
    
    # Create a simple batch/shell script to run the app with common options
    if os_name == 'Windows':
        with open(os.path.join(dist_dir, 'run_brute_force.bat'), 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting Crypto Wallet Brute Force Tool...\n')
            f.write('Crypto_Wallet_Brute_Force.exe --networks BTC ETH BSC TRX --interval 0.5 --report 10\n')
            f.write('pause\n')
    else:
        with open(os.path.join(dist_dir, 'run_brute_force.sh'), 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Crypto Wallet Brute Force Tool..."\n')
            f.write('./Crypto_Wallet_Brute_Force --networks BTC ETH BSC TRX --interval 0.5 --report 10\n')
        # Make the shell script executable
        os.chmod(os.path.join(dist_dir, 'run_brute_force.sh'), 0o755)
    
    print("\nBuild complete!")
    print(f"Executable created in the '{dist_dir}' directory")
    print("You can distribute the entire contents of this directory.")

if __name__ == "__main__":
    main()