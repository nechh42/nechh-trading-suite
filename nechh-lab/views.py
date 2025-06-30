import stripe
from django.conf import settings
from .models import Customer

def create_customer(email, product):
    # Müşteri oluştur veya güncelle
    customer, created = Customer.objects.get_or_create(email=email)
    
    # API key oluştur
    if created:
        customer.api_key = generate_api_key()
    
    # Ürünü ekle
    if product not in customer.products:
        customer.products.append(product)
    
    # Abonelik süresini güncelle (1 ay uzat)
    customer.subscription_end = calculate_subscription_end()
    customer.save()
    
    # Hoş geldin e-postası gönder
    send_welcome_email(email, customer.api_key)