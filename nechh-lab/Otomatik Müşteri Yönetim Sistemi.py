# customer_manager.py
import sqlite3
import stripe

def create_customer(email, product):
    # Stripe müşteri oluştur
    customer = stripe.Customer.create(email=email)
    
    # Yerel veritabanına kaydet
    conn = sqlite3.connect('customers.db')
    c = conn.cursor()
    c.execute('INSERT INTO customers VALUES (?, ?, ?)', 
              (email, product, customer.id))
    conn.commit()
    conn.close()
    
    # API key oluştur ve gönder
    api_key = generate_api_key()
    send_welcome_email(email, api_key)
    return api_key