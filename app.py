from flask import Flask, render_template_string
from binance.client import Client
from dotenv import load_dotenv
import os
import time
import threading

load_dotenv()

app = Flask(__name__)

# Настройки Binance
client = Client(
    api_key=os.getenv('BINANCE_API_KEY'),
    api_secret=os.getenv('BINANCE_API_SECRET'),
    testnet=True
)

# Список отслеживаемых активов
ASSETS = [
    'BTC', 'ETH', 'TWT', 'APT', 'SUI', 'DYDX', '1INCH',
    'OP', 'ARB', 'C98', 'BNB', 'MNT', 'ICP', 'APE',
    'AMB', 'HARRY', 'XCH', 'MAS', 'LINA', 'LDO',
    'SEI', 'LEDOG', '5IRE', 'STRK', 'SQR', 'AEVO', 'OLAS'
]

# Переменная для хранения текущих цен
current_prices = {f"{asset}USDT": "loading..." for asset in ASSETS}

def update_prices():
    """Обновление цен каждые 5 секунд"""
    while True:
        try:
            prices = client.get_all_tickers()
            for asset in ASSETS:
                pair = f"{asset}USDT"
                price_data = next((p for p in prices if p['symbol'] == pair), None)
                if price_data:
                    current_prices[pair] = price_data['price']
        except Exception as e:
            print(f"Error updating prices: {e}")
        time.sleep(5)

# Запускаем обновление цен в фоне
thread = threading.Thread(target=update_prices)
thread.daemon = True
thread.start()

@app.route('/')
def home():
    """Главная страница с автообновлением"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Binance Price Oracle</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body { font-family: Arial; padding: 20px; }
            .price { font-size: 24px; margin: 10px; padding: 10px; background: #f0f0f0; }
        </style>
    </head>
    <body>
        <h1>Live Crypto Prices</h1>
        <p>Updates every 5 seconds</p>
        {% for pair, price in prices.items() %}
        <div class="price">{{ pair }}: {{ price }}</div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, prices=current_prices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
