import datetime
import secrets

def generate_trial_key():
    """7 günlük demo anahtarı oluştur"""
    key = secrets.token_hex(16)
    expiry = datetime.datetime.now() + datetime.timedelta(days=7)
    return {
        'key': f"DEMO_{key}",
        'expiry': expiry,
        'products': ['binance', 'quantum', 'sentiment']  # Tüm botları içerir
    }

# Kullanım
demo_key = generate_trial_key()
print(f"Demo Key: {demo_key['key']}")
print(f"Geçerlilik: {demo_key['expiry']}")