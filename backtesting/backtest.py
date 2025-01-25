import pandas as pd

def backtest_strategy(data, strategy):
    """
    Realiza un backtesting con la estrategia especificada.

    Parámetros:
        data (pd.DataFrame): Datos históricos con columna 'close'.
        strategy (function): Estrategia de trading que devuelve señales ('buy', 'sell', None).

    Retorna:
        tuple: Balance final y ROI (en porcentaje).
    """
    try:
        # Validar el DataFrame de entrada
        if data is None or data.empty:
            raise ValueError("El DataFrame está vacío o no tiene datos suficientes para realizar el backtesting.")
        if 'close' not in data.columns:
            raise ValueError("El DataFrame no contiene la columna 'close'.")

        # Inicializar variables
        initial_balance = 1000  # Capital inicial
        balance = initial_balance
        position = 0  # Número de unidades compradas

        # Iterar a través de los datos históricos
        for i in range(len(data)):
            # Generar señal basada en la estrategia
            signal = strategy(data.iloc[:i+1])  # Pasar los datos hasta el índice actual
            if signal is None:
                continue  # Saltar si no hay señal válida
            if signal not in ['buy', 'sell']:
                raise ValueError(f"Señal inválida generada por la estrategia: {signal}")

            # Ejecutar operación basada en la señal
            if signal == 'buy' and balance > 0 and data['close'].iloc[i] > 0:
                # Comprar usando todo el balance
                position = balance / data['close'].iloc[i]
                balance = 0
            elif signal == 'sell' and position > 0:
                # Vender todas las posiciones
                balance = position * data['close'].iloc[i]
                position = 0

        # Calcular balance final
        final_balance = balance + (position * data['close'].iloc[-1] if position > 0 else 0)
        roi = (final_balance - initial_balance) / initial_balance * 100
        return round(final_balance, 2), round(roi, 2)

    except Exception as e:
        # Registrar y manejar errores
        print(f"Error durante el backtesting: {e}")
        return None, None
