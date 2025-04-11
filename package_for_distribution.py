#!/usr/bin/env python3
"""
Script to package everything for distribution
"""

import os
import shutil
import zipfile
import platform

def main():
    """Main function to create the distribution package"""
    print("Creating distribution package...")
    
    # Create output directories
    os.makedirs("dist", exist_ok=True)
    os.makedirs("package", exist_ok=True)
    
    # Files to include in the package
    files_to_include = [
        # Core files
        "crypto_wallet_gui.py",
        "crypto_wallet_gui_tkinter.py",
        "wallet_generator.py",
        "balance_checker.py",
        "config.py",
        "config_i18n.py",
        "simple_wallet_brute_force.py",
        "example_i18n_usage.py",
        "keywords.txt",
        
        # Support files
        "README.md",
        "FINAL_USER_GUIDE.md",
        "run_gui.bat",
        "run_gui.sh",
        "run_tkinter_gui.bat",
        "run_tkinter_gui.sh",
        "run_vietnamese.bat",
        "run_vietnamese.sh",
        "generated-icon.png",
        
        # Build scripts
        "build_gui_exe.py",
        "build_tkinter_gui_exe.py",
        
        # Log files (if they exist)
        "found_wallets.txt",
        "brute_force_log.txt"
    ]
    
    # Copy files to package directory
    for file in files_to_include:
        if os.path.exists(file):
            try:
                shutil.copy(file, "package/")
                print(f"Copied {file} to package directory")
            except Exception as e:
                print(f"Error copying {file}: {str(e)}")
    
    # Create requirements.txt
    with open("package/requirements.txt", "w") as f:
        f.write("# Required packages\n")
        f.write("bip-utils>=2.9.0\n")
        f.write("requests>=2.25.0\n\n")
        f.write("# Optional - only needed for PyQt5 GUI version\n")
        f.write("# If you plan to use only the Tkinter version, you can skip this\n")
        f.write("pyqt5>=5.15.0\n")
    
    # Create troubleshooting guide
    with open("package/TROUBLESHOOTING.txt", "w") as f:
        f.write("=============================================\n")
        f.write("CRYPTOCURRENCY WALLET BRUTE FORCE TOOL\n")
        f.write("TROUBLESHOOTING GUIDE\n")
        f.write("=============================================\n\n")
        f.write("If you encounter errors when running the executable version of this application,\n")
        f.write("please refer to this troubleshooting guide for assistance.\n\n")
        f.write("-------------------------------------------\n")
        f.write("ERROR: ModuleNotFoundError: No module named 'bip_utils'\n")
        f.write("-------------------------------------------\n\n")
        f.write("This is a common issue with PyInstaller packages where specific dependencies\n")
        f.write("may not be correctly bundled with the executable.\n\n")
        f.write("SOLUTIONS:\n\n")
        f.write("1. RUN FROM SOURCE (RECOMMENDED)\n")
        f.write("   Instead of using the executable, run the Python script directly:\n\n")
        f.write("   a) Make sure Python 3.6+ is installed on your system\n")
        f.write("   b) Install the required dependencies:\n")
        f.write("      pip install bip-utils requests\n")
        f.write("      pip install pyqt5  (only for PyQt5 GUI version)\n")
        f.write("   c) Run the script directly:\n")
        f.write("      python crypto_wallet_gui.py  (for PyQt5 GUI)\n")
        f.write("      python crypto_wallet_gui_tkinter.py  (for Tkinter GUI)\n\n")
        f.write("2. REBUILD THE EXECUTABLE\n")
        f.write("   The build scripts have been updated to explicitly include all required modules.\n\n")
        f.write("   a) Install Python and the necessary packages\n")
        f.write("   b) Run the build script:\n")
        f.write("      python build_gui_exe.py  (for PyQt5 GUI)\n")
        f.write("      python build_tkinter_gui_exe.py  (for Tkinter GUI)\n")
        f.write("   c) The new executable will be in the dist_exe directory\n\n")
        f.write("-------------------------------------------\n")
        f.write("ERROR: API Rate Limit Errors\n")
        f.write("-------------------------------------------\n\n")
        f.write("If you encounter errors related to API rate limits:\n\n")
        f.write("1. Increase the request interval in the settings (try 2.0 or higher)\n")
        f.write("2. Try checking fewer networks simultaneously\n")
        f.write("3. Some API endpoints may require API keys (see the config.py file)\n\n")
        f.write("-------------------------------------------\n")
        f.write("ERROR: Other module import errors\n")
        f.write("-------------------------------------------\n\n")
        f.write("If you encounter other missing module errors, make sure all dependencies are installed:\n\n")
        f.write("1. Install all dependencies:\n")
        f.write("   pip install -r requirements.txt\n\n")
        f.write("2. Install any specific missing module:\n")
        f.write("   pip install [module_name]\n\n")
        f.write("-------------------------------------------\n")
        f.write("NEED MORE HELP?\n")
        f.write("-------------------------------------------\n\n")
        f.write("For more detailed information about using this tool, please refer to the full\n")
        f.write("documentation in the README.md file or visit the project repository.\n\n")
        f.write("Remember that this tool is for educational purposes only. The probability\n")
        f.write("of randomly generating a seed phrase that corresponds to a wallet with funds\n")
        f.write("is astronomically low.\n")
    
    # Create README file specifically for the package
    create_package_readme()
    
    # Create ZIP package
    create_zip_package()
    
    print("Distribution package created successfully!")
    print("Files are available in:")
    print(f"- Package directory: {os.path.abspath('package')}")
    print(f"- ZIP file: {os.path.abspath('dist/Crypto_Wallet_Brute_Force_GUI.zip')}")

def create_package_readme():
    """Create a README file specifically for the package"""
    with open("package/README_FIRST.txt", "w") as f:
        f.write("Cryptocurrency Wallet Brute Force Tool - GUI Version\n")
        f.write("=============================================\n\n")
        
        f.write("## Requirements\n\n")
        f.write("- Python 3.6 or higher\n")
        f.write("- Required packages (install with pip using requirements.txt)\n\n")
        
        f.write("## Installation\n\n")
        f.write("1. Install Python from https://www.python.org/downloads/\n")
        f.write("2. Install required packages using:\n")
        f.write("   pip install -r requirements.txt\n\n")
        
        f.write("## Running the Application\n\n")
        f.write("### PyQt5 Version (Advanced UI)\n")
        f.write("- On Windows: Double-click run_gui.bat\n")
        f.write("- On macOS/Linux: Open terminal, navigate to this directory and run:\n")
        f.write("  chmod +x run_gui.sh\n")
        f.write("  ./run_gui.sh\n\n")
        f.write("- Alternatively, run directly with Python:\n")
        f.write("  python crypto_wallet_gui.py\n\n")
        
        f.write("### Tkinter Version (Compatible with Standard Python)\n")
        f.write("- On Windows: Double-click run_tkinter_gui.bat\n")
        f.write("- On macOS/Linux: Open terminal, navigate to this directory and run:\n")
        f.write("  chmod +x run_tkinter_gui.sh\n")
        f.write("  ./run_tkinter_gui.sh\n\n")
        f.write("- Alternatively, run directly with Python:\n")
        f.write("  python crypto_wallet_gui_tkinter.py\n\n")
        
        f.write("## Choosing Between GUI Versions\n\n")
        f.write("- PyQt5 Version: More advanced UI with better styling, requires PyQt5 to be installed\n")
        f.write("- Tkinter Version: Works with standard Python installation, no extra UI libraries needed\n\n")
        
        f.write("## Multilingual Support\n\n")
        f.write("The tool now includes internationalization support with the following languages:\n")
        f.write("- English (default)\n")
        f.write("- Vietnamese (Tiếng Việt)\n\n")
        f.write("To run the tool in Vietnamese language mode:\n")
        f.write("- On Windows: Double-click run_vietnamese.bat\n")
        f.write("- On macOS/Linux: Open terminal, navigate to this directory and run:\n")
        f.write("  chmod +x run_vietnamese.sh\n")
        f.write("  ./run_vietnamese.sh\n\n")
        f.write("- Alternatively, use the command line argument:\n")
        f.write("  python simple_wallet_brute_force.py --language vi\n\n")
        f.write("## Internationalization Example\n\n")
        f.write("The package includes an example script (example_i18n_usage.py) that demonstrates\n")
        f.write("how to use the internationalization features:\n\n")
        f.write("- Run with default language (English):\n")
        f.write("  python example_i18n_usage.py\n\n")
        f.write("- Run with Vietnamese language:\n")
        f.write("  python example_i18n_usage.py --language vi\n\n")
        f.write("This example shows how to use the translation system for your own projects.\n\n")
        f.write("The simplified brute force version (simple_wallet_brute_force.py) includes language switching\n")
        f.write("while the GUI versions are currently available in English only.\n\n")
        
        f.write("## Building a Standalone Executable\n\n")
        f.write("You can build a standalone executable using PyInstaller:\n\n")
        f.write("1. Install PyInstaller:\n")
        f.write("   pip install pyinstaller\n\n")
        f.write("2. Build the executable (PyQt5 version):\n")
        f.write("   pyinstaller --name=Crypto_Wallet_Brute_Force_GUI --onefile --windowed --add-data=\"keywords.txt:.\" crypto_wallet_gui.py\n\n")
        f.write("3. Build the executable (Tkinter version):\n")
        f.write("   pyinstaller --name=Crypto_Wallet_Brute_Force_GUI_Tkinter --onefile --windowed --add-data=\"keywords.txt:.\" crypto_wallet_gui_tkinter.py\n\n")
        
        f.write("## Troubleshooting\n\n")
        f.write("If you encounter any errors while using this tool, particularly when running the\n")
        f.write("executable version, please refer to the TROUBLESHOOTING.txt file included in this package.\n\n")
        f.write("Common issues addressed in the troubleshooting guide:\n")
        f.write("- Missing module errors (particularly 'bip_utils' module not found)\n")
        f.write("- API rate limit errors\n")
        f.write("- PyInstaller packaging issues\n\n")
        f.write("## Disclaimer\n\n")
        f.write("This tool is for educational purposes only. Using it to attempt to gain unauthorized\n")
        f.write("access to cryptocurrency wallets would be illegal and unethical. The probability\n")
        f.write("of randomly generating a seed phrase that corresponds to a wallet with funds is\n")
        f.write("astronomically low.\n")

def create_zip_package():
    """Create a ZIP package of all files"""
    zip_file = os.path.join("dist", "Crypto_Wallet_Brute_Force_GUI.zip")
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from package directory
        for root, _, files in os.walk("package"):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, "package"))

if __name__ == "__main__":
    main()