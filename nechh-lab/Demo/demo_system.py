import datetime
import os
import json

def create_demo_account(email):
    """7 günlük demo hesabı oluştur"""
    expiry = datetime.datetime.now() + datetime.timedelta(days=7)
    demo_key = f"DEMO-{os.urandom(8).hex().upper()}"
    
    with open('demo_accounts.json', 'a') as f:
        account = {
            "email": email,
            "key": demo_key,
            "expiry": expiry.isoformat(),
            "products": ["binance_futures"]
        }
        json.dump(account, f)
        f.write('\n')
    
    return demo_key

# Kullanım örneği
if __name__ == "__main__":
    email = input("E-posta adresinizi girin: ")
    demo_key = create_demo_account(email)
    print(f"7 günlük demo anahtarınız: {demo_key}")
    print("Botu indirip çalıştırırken bu anahtarı kullanın")