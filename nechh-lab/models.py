from django.db import models

class Customer(models.Model):
    email = models.EmailField(unique=True)
    api_key = models.CharField(max_length=100)
    subscription_end = models.DateField()
    products = models.JSONField(default=list)  # ['binance', 'quantum']