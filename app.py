from flask import Flask, jsonify
from binance.client import Client
from dotenv import load_dotenv
import os
import time

load_dotenv()  # Загружаем ключи из .env

app = Flask(__name__)

# Инициализация клиента Binance
client = Client(
    api_key=os.getenv('BINANCE_API_KEY'),
    api_secret=os.getenv('BINANCE_API_SECRET'),
    testnet=True  # Используем тестовую сеть
)

# Список интересующих нас активов (без USDT, добавим его позже)
ASSETS = [
    'BTC', 'ETH', 'TWT', 'APT', 'SUI', 'DYDX', '1INCH', 
    'OP', 'ARB', 'C98', 'BNB', 'MNT', 'ICP', 'APE', 
    'AMB', 'HARRY', 'XCH', 'MAS', 'LINA', 'LDO', 
    'SEI', 'LEDOG', '5IRE', 'STRK', 'SQR', 'AEVO', 'OLAS'
]

@app.route('/prices')
def get_all_prices():
    try:
        # Получаем все текущие цены с Binance
        all_prices = client.get_all_tickers()
        
        # Фильтруем только нужные нам пары (актив/USDT)
        filtered_prices = []
        
        for asset in ASSETS:
            symbol = f"{asset}USDT"
            price_info = next((item for item in all_prices if item['symbol'] == symbol), None)
            
            if price_info:
                filtered_prices.append({
                    'symbol': symbol,
                    'price': price_info['price'],
                    'timestamp': int(time.time() * 1000)
                })
            else:
                filtered_prices.append({
                    'symbol': symbol,
                    'error': 'Trading pair not found'
                })
        
        return jsonify(filtered_prices)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/price/<symbol>')
def get_price(symbol):
    try:
        price = client.get_symbol_ticker(symbol=symbol.upper())
        return jsonify({
            'symbol': symbol.upper(),
            'price': price['price'],
            'timestamp': int(time.time() * 1000)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
