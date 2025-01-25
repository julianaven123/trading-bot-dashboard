import os
from dotenv import load_dotenv
import pandas as pd
from fastapi import FastAPI, HTTPException
from strategies.simple_moving_average import simple_moving_average_strategy
from backtesting.backtest import backtest_strategy
from utils.data_fetcher import fetch_historical_data
import uvicorn
import logging
from chatgpt_api import chat_with_gpt

# Configurar el sistema de logging
logging.basicConfig(
    filename="bot_errors.log",
    level=logging.DEBUG,  # Cambiado a DEBUG para obtener más detalles
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Cargar variables del entorno desde .env
load_dotenv()

# Configuración de claves API
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

if not BINANCE_API_KEY or not BINANCE_API_SECRET:
    raise EnvironmentError("Faltan las claves API en el archivo .env.")

# Parámetros del bot (valores por defecto)
DEFAULT_SYMBOL = "BTC/USDT"  # Par de trading
DEFAULT_TIMEFRAME = "1h"     # Intervalo de tiempo ('1m', '1h', '1d')
DEFAULT_SINCE = "2023-01-01" # Fecha de inicio de datos

# Instancia de FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    """
    Endpoint raíz que verifica que el bot está en ejecución.
    """
    return {"message": "Bot de trading en ejecución"}

@app.get("/run")
def run_bot(symbol: str = DEFAULT_SYMBOL, timeframe: str = DEFAULT_TIMEFRAME, since: str = DEFAULT_SINCE):
    """
    Ejecuta el bot de trading: obtiene datos, realiza backtesting y muestra resultados.
    Permite configurar el símbolo, el intervalo de tiempo y la fecha de inicio.
    """
    try:
        logging.debug("=== Bot de Trading Automático ===")

        # Obtener datos históricos
        logging.debug(f"Obteniendo datos históricos para {symbol} con intervalo {timeframe} desde {since}...")
        data = fetch_historical_data(symbol, timeframe, since)

        if data is None or data.empty:
            raise HTTPException(status_code=400, detail="No se pudieron obtener datos históricos.")

        logging.debug(f"Datos históricos cargados correctamente. Total de filas: {len(data)}")

        # Validar que los datos tengan la columna 'close'
        if 'close' not in data.columns:
            raise ValueError("La columna 'close' no está presente en los datos.")

        # Guardar datos en la carpeta `data`
        os.makedirs("data", exist_ok=True)
        data_path = os.path.join("data", f"{symbol.replace('/', '_')}_{timeframe}.csv")
        data.to_csv(data_path, index=False)
        logging.debug(f"Datos guardados en {data_path}")

        # Realizar backtesting con la estrategia SMA
        logging.debug("Iniciando backtesting con la estrategia Simple Moving Average...")
        final_balance, roi = backtest_strategy(data, simple_moving_average_strategy)

        if final_balance is None or roi is None:
            raise HTTPException(status_code=500, detail="Error en el backtesting: No se pudo calcular el balance final o el ROI.")

        result = {
            "balance_final": round(final_balance, 2),
            "roi": round(roi, 2),
            "message": "Backtesting completado"
        }

        logging.debug("Backtesting completado con éxito.")
        return result

    except Exception as e:
        logging.error(f"Error al ejecutar el bot: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ha ocurrido un error al ejecutar el bot. Consulte el archivo de log.")

@app.get("/chat")
def chat_endpoint(message: str):
    """
    Endpoint para interactuar con el chatbot.
    """
    try:
        response = chat_with_gpt(message)
        return {"response": response}
    except Exception as e:
        logging.error(f"Error al interactuar con el chatbot: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ha ocurrido un error al interactuar con el chatbot. Consulte el archivo de log.")

# Punto de entrada del script
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
