import os
import time
import threading
import requests
import pandas as pd
from flask import Flask, jsonify, send_file
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

ASSETS = [
    'BTC', 'ETH', 'TWT', 'APT', 'SUI', 'DYDX', '1INCH',
    'OP', 'ARB', 'C98', 'BNB', 'MNT', 'ICP', 'APE',
    'AMB', 'HARRY', 'XCH', 'MAS', 'LINA', 'LDO',
    'SEI', 'LEDOG', '5IRE', 'STRK', 'SQR', 'AEVO', 'OLAS'
]

# Хранилище цен (только ETH и DEX)
current_prices = {'ETH': {}, 'DEX': {}}

def get_cmc_dex_prices():
    """Получение DEX-котировок через CoinMarketCap"""
    url = "https://pro-api.coinmarketcap.com/v4/dex/spot-pairs/latest"
    headers = {'X-CMC_PRO_API_KEY': os.getenv('COINMARKETCAP_API_KEY')}
    response = requests.get(url, headers=headers)
    return response.json()['data'] if response.status_code == 200 else None

def fetch_prices():
    """Обновление цен ETH-пар и DEX"""
    prices = {'ETH': {}, 'DEX': {}}
    
    # Binance ETH-пары
    try:
        binance_prices = Client(
            api_key=os.getenv('BINANCE_API_KEY'),
            api_secret=os.getenv('BINANCE_API_SECRET'),
            testnet=True
        ).get_all_tickers()
        
        for asset in ASSETS:
            if asset != 'ETH':
                pair = f"{asset}ETH"
                price_data = next((p for p in binance_prices if p['symbol'] == pair), None)
                prices['ETH'][asset] = price_data['price'] if price_data else None
    except Exception as e:
        print(f"Binance ETH pairs error: {e}")

    # DEX-котировки (ETH-пары)
    dex_data = get_cmc_dex_prices()
    if dex_data:
        for asset in ASSETS:
            dex_pair = next(
                (p for p in dex_data 
                 if p['base_symbol'] == asset and p['quote_symbol'] == 'ETH'),
                None
            )
            prices['DEX'][asset] = dex_pair['price'] if dex_pair else None

    return prices

# Фоновое обновление цен
def price_updater():
    while True:
        global current_prices
        current_prices = fetch_prices()
        time.sleep(120)  # Обновление каждые 2 минуты

threading.Thread(target=price_updater, daemon=True).start()

# Логирование в CSV
def log_prices():
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df = pd.DataFrame({
            'Asset': ASSETS,
            'Price_ETH': [current_prices['ETH'].get(a) for a in ASSETS],
            'DEX_Price_ETH': [current_prices['DEX'].get(a) for a in ASSETS],
            'Timestamp': timestamp
        })
        df.to_csv('prices_log.csv', mode='a', header=not os.path.exists('prices_log.csv'), index=False)
        time.sleep(120)  # Логи каждые 2 минуты

threading.Thread(target=log_prices, daemon=True).start()

# Маршруты
@app.route('/')
def home():
    return jsonify({
        "endpoints": {
            "/prices": "Все котировки в ETH",
            "/dex": "DEX-котировки",
            "/log": "Скачать историю цен"
        }
    })

@app.route('/prices')
def get_prices():
    return jsonify(current_prices['ETH'])

@app.route('/dex')
def get_dex():
    return jsonify(current_prices['DEX'])

@app.route('/log')
def download_log():
    return send_file('prices_log.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
