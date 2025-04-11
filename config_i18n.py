"""
Configuration file for the cryptocurrency wallet brute force tool.
Contains API endpoints, settings, and internationalization support.
"""

# API Configuration for different networks
API_CONFIG = {
    'BTC': {
        'url': 'https://blockchain.info/balance?active={address}',
        'key': None
    },
    'ETH': {
        'url': 'https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={key}',
        'key': None
    },
    'BSC': {
        'url': 'https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest&apikey={key}',
        'key': None
    },
    'TRX': {
        'url': 'https://api.trongrid.io/v1/accounts/{address}',
        'key': None
    }
}

# Conversion factors for different cryptocurrencies
CONVERSION_FACTORS = {
    'BTC': 1e8,  # satoshi to BTC
    'ETH': 1e18,  # wei to ETH
    'BSC': 1e18,  # wei to BNB
    'TRX': 1e6   # sun to TRX
}

# Language translations
TRANSLATIONS = {
    'en': {
        'reading_keywords': 'Reading BIP-39 keywords...',
        'starting_process': 'Starting brute force process...',
        'stopping_process': 'Stopping brute force process...',
        'seed_phrase': 'Seed phrase',
        'wallet_address': 'Wallet address',
        'balance': 'Balance',
        'attempts': 'Attempts',
        'speed': 'Speed',
        'found': 'Found',
        'attempts_per_sec': 'attempts/sec',
        'press_enter_to_stop': 'Press Enter to stop...',
        'wallet_found': 'WALLET WITH BALANCE FOUND!',
        'saved_to_file': 'Details saved to',
        'require_keywords': 'Need at least 12 keywords in the file!',
        'stats': 'Stats',
        'error_api_rate_limit': 'API rate limit error, increasing interval...',
        'error_connection': 'Connection error',
        'invalid_mnemonic': 'Invalid mnemonic, retrying...'
    },
    'vi': {
        'reading_keywords': 'Đang đọc từ khóa BIP-39...',
        'starting_process': 'Bắt đầu quá trình tìm kiếm...',
        'stopping_process': 'Đang dừng quá trình tìm kiếm...',
        'seed_phrase': 'Cụm từ hạt giống',
        'wallet_address': 'Địa chỉ ví',
        'balance': 'Số dư',
        'attempts': 'Số lần thử',
        'speed': 'Tốc độ',
        'found': 'Đã tìm thấy',
        'attempts_per_sec': 'lần thử/giây',
        'press_enter_to_stop': 'Nhấn Enter để dừng...',
        'wallet_found': 'ĐÃ TÌM THẤY VÍ CÓ SỐ DƯ!',
        'saved_to_file': 'Chi tiết đã được lưu vào',
        'require_keywords': 'Cần ít nhất 12 từ khóa trong file!',
        'stats': 'Thống kê',
        'error_api_rate_limit': 'Lỗi giới hạn API, tăng khoảng thời gian...',
        'error_connection': 'Lỗi kết nối',
        'invalid_mnemonic': 'Cụm từ không hợp lệ, thử lại...'
    }
}

# Default language
DEFAULT_LANGUAGE = 'en'

def get_text(key, language=DEFAULT_LANGUAGE):
    """
    Get translated text for a specific key
    
    Args:
        key (str): The translation key
        language (str): Language code (default: DEFAULT_LANGUAGE)
        
    Returns:
        str: Translated text
    """
    if language not in TRANSLATIONS:
        language = DEFAULT_LANGUAGE
    
    return TRANSLATIONS[language].get(key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))