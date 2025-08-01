import os
import time
import threading
import requests
from flask import Flask, jsonify
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime

# Инициализация
load_dotenv()
app = Flask(__name__)

# Конфигурация
ASSETS = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']
UPDATE_INTERVAL = 10  # секунд
MAX_HISTORY = 100     # записей

# Глобальное хранилище
current_prices = {'Binance_ETH': {}, 'CMC_DEX': {}}
price_history = []

def get_cmc_dex_prices():
    """Получение цен через CoinMarketCap DEX API"""
    url = "https://pro-api.coinmarketcap.com/v4/dex/spot-pairs/latest"
    headers = {'X-CMC_PRO_API_KEY': os.getenv('COINMARKETCAP_API_KEY')}
    try:
        response = requests.get(url, headers=headers)
        return response.json()['data'] if response.status_code == 200 else None
    except:
        return None

def fetch_prices():
    """Сбор цен с Binance и CMC"""
    prices = {'Binance_ETH': {}, 'CMC_DEX': {}}
    
    # Binance ETH-пары
    try:
        binance = Client(
            api_key=os.getenv('BINANCE_API_KEY'),
            api_secret=os.getenv('BINANCE_API_SECRET'),
            testnet=True
        )
        tickers = binance.get_all_tickers()
        for asset in ASSETS:
            if asset != 'ETH':
                pair = f"{asset}ETH"
                price = next((p for p in tickers if p['symbol'] == pair), None)
                prices['Binance_ETH'][asset] = price['price'] if price else None
    except Exception as e:
        print(f"Binance error: {e}")

    # CMC DEX-пары
    dex_data = get_cmc_dex_prices()
    if dex_data:
        for asset in ASSETS:
            pair = next((p for p in dex_data if p['base_symbol'] == asset and p['quote_symbol'] == 'ETH'), None)
            prices['CMC_DEX'][asset] = pair['price'] if pair else None

    return prices

def background_updater():
    """Фоновая задача обновления цен"""
    global current_prices, price_history
    while True:
        new_prices = fetch_prices()
        current_prices = new_prices
        price_history.append({
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'prices': new_prices
        })
        # Ограничиваем размер истории
        if len(price_history) > MAX_HISTORY:
            price_history.pop(0)
        time.sleep(UPDATE_INTERVAL)

# Маршруты API
@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "endpoints": {
            "/prices": "Current prices",
            "/history": "Price history (last 100 entries)",
            "/assets": "Supported assets"
        }
    })

@app.route('/prices')
def prices():
    return jsonify(current_prices)

@app.route('/history')
def history():
    return jsonify({
        "count": len(price_history),
        "history": price_history
    })

@app.route('/assets')
def assets():
    return jsonify({"assets": ASSETS})

# Запуск фонового обновления
thread = threading.Thread(target=background_updater)
thread.daemon = True
thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
