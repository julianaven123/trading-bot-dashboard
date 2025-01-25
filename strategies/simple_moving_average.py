import pandas as pd
import numpy as np

def simple_moving_average_strategy(data: pd.DataFrame, short_window=20, long_window=50):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['close']
    signals['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1).mean()
    signals['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1).mean()

    signals['signal'] = 0.0
    signals.loc[data.index[short_window:], 'signal'] = np.where(
        signals.loc[data.index[short_window:], 'short_mavg'] > signals.loc[data.index[short_window:], 'long_mavg'], 
        1.0, 0.0
    )
    signals['positions'] = signals['signal'].diff()

    return signals

def simple_moving_average_decision(data):
    if len(data) < 20:
        return None  # No tomar decisiones sin suficientes datos
    short_ma = data['close'].iloc[-10:].mean()
    long_ma = data['close'].iloc[-20:].mean()
    if short_ma > long_ma:
        return 'buy'
    elif short_ma < long_ma:
        return 'sell'
    return None
