import sys
import os
import time
from itertools import product
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()

# Agregar la raíz del proyecto al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import ccxt
from backtesting.backtest import backtest_strategy
from utils.data_fetcher import fetch_historical_data

# Validar claves API
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

if not api_key or not api_secret:
    raise ValueError("Las credenciales de la API de Binance no están configuradas correctamente. Revisa el archivo .env.")

# Configuración para operación en tiempo real
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
})

# Función para obtener precios en vivo
def fetch_live_data(symbol, timeframe, limit=50):
    """
    Obtiene datos OHLCV en tiempo real desde Binance.
    """
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error al obtener datos en vivo: {e}")
        return None

# Estrategia de promedio móvil optimizado con stop-loss y drawdown
def optimized_moving_average_decision(data, state, short_window=3, long_window=5, stop_loss_percent=0.95, max_drawdown_percent=0.1):
    """
    Genera una señal de compra o venta basada en promedios móviles, evitando operaciones consecutivas innecesarias.
    """
    # Verificar que haya suficientes datos para calcular los promedios
    if len(data) < long_window:
        return None

    # Calcular promedios móviles
    short_ma = data['close'].iloc[-short_window:].mean()
    long_ma = data['close'].iloc[-long_window:].mean()

    # Controlar el drawdown máximo
    if state['max_balance'] is not None:
        drawdown = (state['max_balance'] - data['close'].iloc[-1]) / state['max_balance']
        if drawdown > max_drawdown_percent:
            state['previous_signal'] = 'sell'
            return 'sell'

    # Evitar señales consecutivas innecesarias
    if short_ma > long_ma and state['previous_signal'] != 'buy':
        state['previous_signal'] = 'buy'
        state['stop_loss'] = data['close'].iloc[-1] * stop_loss_percent  # Stop-loss dinámico
        state['max_balance'] = max(state['max_balance'] or 0, data['close'].iloc[-1])  # Actualizar balance máximo
        return 'buy'
    elif short_ma < long_ma and state['previous_signal'] != 'sell':
        state['previous_signal'] = 'sell'
        state['stop_loss'] = None
        return 'sell'
    return None

# Función para ejecutar órdenes en Binance
def execute_order(signal, symbol, state):
    """
    Ejecuta una orden de compra o venta en Binance.
    """
    try:
        if signal == "buy":
            balance = exchange.fetch_balance()
            usdt_balance = balance['free']['USDT']
            price = exchange.fetch_ticker(symbol)['last']
            amount = usdt_balance / price

            if usdt_balance > 1:  # Ajuste para operar con 99 USDT
                order = exchange.create_market_buy_order(symbol, round(amount, 6))
                print(f"Orden de compra ejecutada: {order}")
        elif signal == "sell":
            balance = exchange.fetch_balance()
            asset = symbol.split('/')[0]
            asset_balance = balance['free'][asset]

            if asset_balance > 0.0001:  # Ajuste para pequeñas cantidades de BTC
                order = exchange.create_market_sell_order(symbol, round(asset_balance, 6))
                print(f"Orden de venta ejecutada: {order}")
    except Exception as e:
        print(f"Error al ejecutar la orden: {e}")

# Función para probar conexión con Binance
def test_binance_connection():
    """
    Verifica la conexión con Binance y muestra el balance actual.
    """
    try:
        print("\n=== Probando conexión con Binance ===")
        balance = exchange.fetch_balance()
        usdt_balance = balance['free']['USDT']
        btc_balance = balance['free']['BTC']
        print(f"Conexión exitosa. Balance disponible en USDT: {usdt_balance}, BTC: {btc_balance}")
    except Exception as e:
        print(f"Error al conectar con Binance: {e}")

# Ejecutar estrategia en tiempo real
def run_live_trading(symbol, timeframe, short_window, long_window, stop_loss, max_drawdown):
    print(f"\n=== Iniciando trading en tiempo real para {symbol} en {timeframe} ===")
    state = {'previous_signal': None, 'stop_loss': None, 'max_balance': None}

    while True:
        data = fetch_live_data(symbol, timeframe)
        if data is None or data.empty:
            print("No se pudieron obtener datos en vivo. Reintentando...")
            time.sleep(10)
            continue

        signal = optimized_moving_average_decision(data, state, short_window, long_window, stop_loss, max_drawdown)

        if signal:
            print(f"[{pd.Timestamp.now()}] Señal generada: {signal}")
            execute_order(signal, symbol, state)

        time.sleep(60)  # Esperar antes de la próxima iteración

# Configuración inicial para trading en tiempo real
symbol = "BTC/USDT"
timeframe = "1m"
short_window = 9
long_window = 13
stop_loss = 0.90
max_drawdown = 0.05

# Ejecutar el trading en tiempo real
if __name__ == "__main__":
    test_binance_connection()
    run_live_trading(symbol, timeframe, short_window, long_window, stop_loss, max_drawdown)
