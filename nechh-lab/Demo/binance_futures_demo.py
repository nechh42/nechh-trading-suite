import os
import datetime
import json
import time

def check_demo_license(demo_key):
    """Demo lisans kontrolü"""
    try:
        with open('demo_accounts.json', 'r') as f:
            for line in f:
                account = json.loads(line)
                if account['key'] == demo_key:
                    expiry = datetime.datetime.fromisoformat(account['expiry'])
                    return datetime.datetime.now() < expiry
        return False
    except FileNotFoundError:
        return False

def main():
    print("Binance Futures Bot Başlatılıyor...")
    demo_key = input("Demo anahtarınızı girin: ")
    
    if check_demo_license(demo_key):
        print("7 günlük demo sürümü kullanıyorsunuz")
        print("Bot çalışıyor... (Gerçek işlem yapmaz)")
        
        # Burada gerçek bot mantığı olacak
        while True:
            print(f"{time.strftime('%H:%M:%S')} - Piyasa taranıyor...")
            time.sleep(10)
    else:
        print("Geçersiz veya süresi dolmuş demo anahtarı!")

if __name__ == "__main__":
    main()