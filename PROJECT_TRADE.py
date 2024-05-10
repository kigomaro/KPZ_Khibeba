import pandas as pd
import numpy as np
import ta
from dataclasses import dataclass

@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    side: str
    profit: float = None

np.random.seed(42)

# Генерация данных
dates = pd.date_range(start="2022-01-01", end="2023-12-31", freq='min')
prices = np.random.lognormal(mean=0, sigma=0.01, size=len(dates)) + 50
prices = prices.cumsum()
volumes = np.random.randint(100, 1000, size=len(dates))

data = pd.DataFrame({
    'time': dates, 
    'open': prices + np.random.normal(0, 2, size=len(prices)),
    'high': prices + np.random.normal(0, 2, size=len(prices)),
    'low': prices - np.random.normal(0, 2, size=len(prices)),
    'close': prices,
    'volume': volumes
})
data.set_index('time', inplace=True)

def apply_indicators(dataframe):
    dataframe['ema5'] = ta.trend.EMAIndicator(dataframe['close'], window=5).ema_indicator()
    dataframe['ema10'] = ta.trend.EMAIndicator(dataframe['close'], window=10).ema_indicator()
    dataframe['rsi14'] = ta.momentum.RSIIndicator(dataframe['close'], window=14).rsi()
    return dataframe

data = apply_indicators(data)

def create_signals(dataframe):
    signals = []
    for i in range(1, len(dataframe)):
        ema5 = dataframe['ema5'].iloc[i]
        ema10 = dataframe['ema10'].iloc[i]
        rsi14 = dataframe['rsi14'].iloc[i]
        if ema5 > ema10 and rsi14 > 50:
            signals.append({'time': dataframe.index[i], 'type': 'buy', 'price': dataframe['close'].iloc[i]})
        elif ema5 < ema10 and rsi14 < 50:
            signals.append({'time': dataframe.index[i], 'type': 'sell', 'price': dataframe['close'].iloc[i]})
    return signals

signals = create_signals(data)

def backtest(signals, data):
    investment = 10000
    cash = investment
    position = 0
    trades = []
    open_trade = None

    for signal in signals:
        price = signal['price']
        if signal['type'] == 'buy' and cash > 0:
            position = cash / price
            cash = 0
            open_trade = Trade(entry_time=signal['time'], entry_price=price, side='buy', exit_time=None, exit_price=None, profit=None)
        elif signal['type'] == 'sell' and position > 0:
            cash = position * price
            if open_trade:
                open_trade.exit_time = signal['time']
                open_trade.exit_price = price
                open_trade.profit = (price - open_trade.entry_price) * position
                trades.append(open_trade)
            position = 0
            open_trade = None

    if position > 0 and open_trade:
        open_trade.exit_time = data.index[-1]
        open_trade.exit_price = data['close'].iloc[-1]
        open_trade.profit = (open_trade.exit_price - open_trade.entry_price) * position
        trades.append(open_trade)
        cash = position * open_trade.exit_price

    final_value = cash
    return final_value, trades

def calculate_profit_factor(trades):
    total_profit = sum(trade.profit for trade in trades if trade.profit > 0)
    total_loss = abs(sum(trade.profit for trade in trades if trade.profit < 0))
    if total_loss == 0:
        return float('inf') 
    return total_profit / total_loss

def calculate_winrate(trades):
    wins = sum(1 for trade in trades if trade.profit > 0)
    total_trades = len(trades)
    if total_trades == 0:
        return 0  
    return (wins / total_trades) * 100



final_value, trades = backtest(signals, data)
profit_factor = calculate_profit_factor(trades)
winrate = calculate_winrate(trades)
print(f"Initial investment: $10000, Final value: ${final_value:.2f}")
print(f"Profit Factor: {profit_factor:.2f}")
print(f"Winrate: {winrate:.2f}%")
# Сохранение сгенерированных данных
def save_generated_data(dataframe):
    dataframe.to_csv('generated_data.csv', index=True)
    print("Generated data saved to 'generated_data.csv'.")

# Применение индикаторов и сохранение данных
data = apply_indicators(data)
save_generated_data(data)


def trades_to_dataframe(trades):
    columns = ['Entry Time', 'Exit Time', 'Entry Price', 'Exit Price', 'Side', 'Profit']
    trade_data = [[trade.entry_time, trade.exit_time, trade.entry_price, trade.exit_price, trade.side, trade.profit] for trade in trades if trade.profit is not None]
    return pd.DataFrame(trade_data, columns=columns)

trades_df = trades_to_dataframe(trades)
trades_df.to_csv('trade_results.csv', index=False)
print(trades_df)
