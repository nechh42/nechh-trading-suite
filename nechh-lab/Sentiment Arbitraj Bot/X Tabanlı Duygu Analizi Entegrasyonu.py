import time
import logging
import ccxt
import pandas as pd
import ta
import requests
import os
from dotenv import load_dotenv
from transformers import pipeline
from datetime import datetime, timedelta
import tweepy  # Gerçek Twitter API için

# .env dosyasından çevresel değişkenleri yükle
load_dotenv()

class NewsArbHybrid:
    def __init__(self):
        self.binance = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'enableRateLimit': True
        })
        self.capital = 100  # $100
        self.fee_rate = 0.001  # %0.1 işlem ücreti
        self.max_risk = 0.01  # Maksimum risk: %1
        self.volatility_threshold = 0.5  # ATR eşiği
        self.sentiment_threshold = 0.7  # Sentiment tetikleyici (0.7'e yükseltildi)
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis", 
            model="finiteautomata/bertweet-base-sentiment-analysis"  # Crypto-özel model
        )
        # Twitter API için kimlik doğrulama
        self.twitter_auth = tweepy.OAuth1UserHandler(
            os.getenv('TWITTER_API_KEY'),
            os.getenv('TWITTER_API_SECRET'),
            os.getenv('TWITTER_ACCESS_TOKEN'),
            os.getenv('TWITTER_ACCESS_SECRET')
        )
        self.twitter_api = tweepy.API(self.twitter_auth)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    def fetch_tweets(self, hashtag="#BTC", count=50):
        """Twitter'dan son tweet'leri çek"""
        try:
            tweets = []
            # Son 2 saat içindeki tweet'ler
            since_time = datetime.utcnow() - timedelta(hours=2)
            for tweet in tweepy.Cursor(
                self.twitter_api.search_tweets,
                q=hashtag,
                lang="en",
                since=since_time.strftime("%Y-%m-%d")
            ).items(count):
                tweets.append(tweet.text)
            return tweets
        except Exception as e:
            logging.error(f"Tweet çekme hatası: {e}")
            return []

    def get_sentiment(self):
        """Tweet'lerden sentiment skoru hesapla"""
        tweets = self.fetch_tweets()
        if not tweets:
            logging.info("Tweet bulunamadı, sentiment 0.")
            return 0
        
        scores = []
        for tweet in tweets:
            try:
                result = self.sentiment_analyzer(tweet)[0]
                # Model çıktısı: LABEL_0 (neg), LABEL_1 (nötr), LABEL_2 (poz)
                if result['label'] == 'LABEL_2':  # Pozitif
                    scores.append(result['score'])
                elif result['label'] == 'LABEL_0':  # Negatif
                    scores.append(-result['score'])
                # Nötrleri atla
            except Exception as e:
                logging.error(f"Sentiment analiz hatası: {e}")
        
        if not scores:
            return 0
        return sum(scores) / len(scores)  # Ortalama skor

    def fetch_prices(self, symbol='BTC/USDT'):
        """Binance'ten fiyatları çek"""
        try:
            ticker = self.binance.fetch_ticker(symbol)
            return {'bid': ticker['bid'], 'ask': ticker['ask']}
        except Exception as e:
            logging.error(f"Fiyat alınırken hata: {e}")
            return None

    def get_volatility(self, symbol='BTC/USDT', timeframe='1m', limit=100):
        """Volatiliteyi (ATR) hesapla"""
        try:
            ohlcv = self.binance.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
            return df['atr'].iloc[-1]
        except Exception as e:
            logging.error(f"Volatilite hesaplanırken hata: {e}")
            return None

    def find_arbitrage_opportunity(self, symbol='BTC/USDT'):
        """Arbitraj fırsatlarını tespit et"""
        sentiment = self.get_sentiment()
        logging.info(f"Sentiment Skoru: {sentiment:.2f}")
        if abs(sentiment) < self.sentiment_threshold:
            logging.info(f"Düşük sentiment skoru ({sentiment:.2f}), arbitraj taraması durduruldu.")
            return None

        prices = self.fetch_prices(symbol)
        if not prices:
            return None

        atr = self.get_volatility(symbol)
        if not atr:
            return None

        # Risk yönetimi: Volatiliteye göre pozisyon büyüklüğü
        risk_factor = 0.02 if atr > self.volatility_threshold else 0.005
        amount = (self.capital * min(self.max_risk, risk_factor)) / prices['ask']

        # Binance içi arbitraj
        bid, ask = prices['bid'], prices['ask']
        spread = bid - ask
        fees = (ask * self.fee_rate) + (bid * self.fee_rate)
        net_profit = spread - fees

        if net_profit > 0:
            return {
                'buy_price': ask,
                'sell_price': bid,
                'amount': amount,
                'net_profit': net_profit * amount,
                'atr': atr,
                'sentiment': sentiment
            }
        return None

    def execute_trade(self, opportunity, symbol='BTC/USDT'):
        """PAPER TRADE: Gerçek emir yerine log yaz (güvenlik için)"""
        if not opportunity:
            return False
        logging.info(f"ALIM: {opportunity['amount']:.6f} BTC @ {opportunity['buy_price']}")
        logging.info(f"SATIM: {opportunity['amount']:.6f} BTC @ {opportunity['sell_price']}")
        logging.info(f"TAHMİNİ KÂR: ${opportunity['net_profit']:.2f}, Sentiment: {opportunity['sentiment']:.2f}")
        return True

    def run(self, symbol='BTC/USDT', interval=60):
        """Botu çalıştır (PAPER TRADE modunda)"""
        logging.info("=== HABER ARBITRAJ BOTU BAŞLATILDI (PAPER TRADE) ===")
        while True:
            try:
                opportunity = self.find_arbitrage_opportunity(symbol)
                if opportunity:
                    self.execute_trade(opportunity, symbol)
                else:
                    logging.info("Arbitraj fırsatı bulunamadı.")
                time.sleep(interval)
            except Exception as e:
                logging.error(f"Hata oluştu: {str(e)}")
                time.sleep(interval)

if __name__ == "__main__":
    bot = NewsArbHybrid()
    bot.run()