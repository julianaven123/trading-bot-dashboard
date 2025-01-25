import ccxt
import pandas as pd
from datetime import datetime

def fetch_historical_data(symbol, timeframe, since):
    """
    Obtiene datos históricos de Binance a través de CCXT.
    
    Parámetros:
        symbol (str): El par de trading (ej. "BTC/USDT").
        timeframe (str): El intervalo de tiempo (ej. "1h", "1d").
        since (str): Fecha de inicio en formato ISO (ej. "2023-01-01").
    
    Retorna:
        pd.DataFrame: Datos OHLCV en un DataFrame.
    """
    try:
        exchange = ccxt.binance()
        since_timestamp = exchange.parse8601(f"{since}T00:00:00Z")
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since_timestamp)

        if not ohlcv:
            raise ValueError("No se recibieron datos de la API.")

        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error al obtener datos históricos: {e}")
        return None
