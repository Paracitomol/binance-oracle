from flask import Flask, jsonify
from binance.client import Client
from dotenv import load_dotenv
import os
import time

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)

# Инициализация клиента Binance
client = Client(
    api_key=os.getenv('BINANCE_API_KEY'),
    api_secret=os.getenv('BINANCE_API_SECRET'),
    testnet=True  # Используем Testnet API
)

# Список отслеживаемых активов
ASSETS = [
    'BTC', 'ETH', 'TWT', 'APT', 'SUI', 'DYDX', '1INCH',
    'OP', 'ARB', 'C98', 'BNB', 'MNT', 'ICP', 'APE',
    'AMB', 'HARRY', 'XCH', 'MAS', 'LINA', 'LDO',
    'SEI', 'LEDOG', '5IRE', 'STRK', 'SQR', 'AEVO', 'OLAS'
]

@app.route('/')
def home():
    """Главная страница с инструкцией"""
    return jsonify({
        "message": "Binance Testnet Price API",
        "endpoints": {
            "/prices": "Get all asset prices",
            "/price/<symbol>": "Get price for specific asset (e.g. /price/BTCUSDT)"
        },
        "available_assets": ASSETS
    })

@app.route('/prices')
def get_prices():
    """Получение цен всех активов"""
    try:
        # Получаем все текущие цены с Binance
        all_prices = client.get_all_tickers()
        
        # Фильтруем только нужные нам пары
        result = []
        for asset in ASSETS:
            symbol = f"{asset}USDT"
            price_data = next(
                (p for p in all_prices if p['symbol'] == symbol),
                None
            )
            
            if price_data:
                result.append({
                    "symbol": symbol,
                    "price": price_data["price"],
                    "timestamp": int(time.time() * 1000)
                })
            else:
                result.append({
                    "symbol": symbol,
                    "error": "Trading pair not found",
                    "timestamp": int(time.time() * 1000)
                })
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to fetch prices"
        }), 500

@app.route('/price/<symbol>')
def get_single_price(symbol):
    """Получение цены конкретного актива"""
    try:
        # Добавляем USDT, если его нет в символе
        if not symbol.upper().endswith('USDT'):
            symbol = f"{symbol.upper()}USDT"
        
        price = client.get_symbol_ticker(symbol=symbol)
        return jsonify({
            "symbol": symbol,
            "price": price["price"],
            "timestamp": int(time.time() * 1000)
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": f"Failed to fetch price for {symbol}"
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
