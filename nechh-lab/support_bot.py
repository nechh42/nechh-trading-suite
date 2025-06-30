import telebot
from django.conf import settings

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Nechh Lab Destek Merkezi! Sorunuzu yazın.")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    # Soruyu destek sistemine kaydet
    save_question(message.from_user.id, message.text)
    bot.reply_to(message, "Sorunuz kaydedildi. En kısa sürede döneceğiz!")

bot.polling()