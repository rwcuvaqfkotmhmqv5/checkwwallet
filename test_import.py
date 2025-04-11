import sys
print('Python version:', sys.version)

try:
    import bip_utils
    print('bip_utils import successful')
    print('bip_utils version:', bip_utils.__version__ if hasattr(bip_utils, '__version__') else 'Version not available')
    print('Available components:')
    print('- Bip39SeedGenerator:', 'Available' if hasattr(bip_utils, 'Bip39SeedGenerator') else 'Not available')
    print('- Bip44:', 'Available' if hasattr(bip_utils, 'Bip44') else 'Not available')
    print('- Bip44Coins:', 'Available' if hasattr(bip_utils, 'Bip44Coins') else 'Not available')
except ImportError as e:
    print(f'bip_utils import error: {e}')