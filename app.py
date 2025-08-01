import os
import time
import threading
import requests
from flask import Flask, jsonify
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime

# Настройка
load_dotenv()
app = Flask(__name__)

ASSETS = [
    'BTC', 'ETH', 'TWT', 'APT', 'SUI', 'DYDX', '1INCH',
    'OP', 'ARB', 'C98', 'BNB', 'MNT', 'ICP', 'APE',
    'AMB', 'HARRY', 'XCH', 'MAS', 'LINA', 'LDO',
    'SEI', 'LEDOG', '5IRE', 'STRK', 'SQR', 'AEVO', 'OLAS'
]

# Хранилище данных
prices_log = []

def get_binance_prices():
    """Получаем цены с Binance"""
    client = Client(
        os.getenv('BINANCE_API_KEY'),
        os.getenv('BINANCE_API_SECRET'),
        testnet=True
    )
    return client.get_all_tickers()

def get_cmc_dex_prices():
    """Получаем цены с CoinMarketCap DEX"""
    url = "https://pro-api.coinmarketcap.com/v4/dex/spot-pairs/latest"
    headers = {'X-CMC_PRO_API_KEY': os.getenv('COINMARKETCAP_API_KEY')}
    return requests.get(url, headers=headers).json()

def save_to_log():
    """Сохраняем данные в файл"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('prices_log.csv', 'a') as f:
        for asset in ASSETS:
            f.write(f"{timestamp},{asset},ETH,{current_prices.get(asset)}\n")

def update_prices():
    """Обновляем цены каждые 2 минуты"""
    while True:
        try:
            # Получаем данные
            binance_data = get_binance_prices()
            cmc_data = get_cmc_dex_prices()
            
            # Обрабатываем и сохраняем
            process_prices(binance_data, cmc_data)
            save_to_log()
            
        except Exception as e:
            print(f"Ошибка: {e}")
        
        time.sleep(120)  # 2 минуты

# Запускаем в фоне
thread = threading.Thread(target=update_prices)
thread.daemon = True
thread.start()

@app.route('/')
def home():
    return "Crypto Oracle работает! Используйте /prices"

@app.route('/prices')
def prices():
    return jsonify(prices_log[-1] if prices_log else {})

if __name__ == '__main__':
    app.run(port=3000)
