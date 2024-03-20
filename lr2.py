import pandas as pd
from binance import Client

def calculate_rsi(prices, period):
    deltas = prices.diff().dropna()
    gains = deltas.where(deltas > 0, 0)
    losses = -deltas.where(deltas < 0, 0)
    average_gain = gains.rolling(window=period).mean()
    average_loss = losses.rolling(window=period).mean()
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_rsi_data(asset, periods):
    client = Client()
    k_lines = client.get_historical_klines(
        symbol=asset,
        interval=Client.KLINE_INTERVAL_1MINUTE,
        start_str="1 day ago UTC",
        end_str="now UTC"
    )
    k_lines = pd.DataFrame(k_lines)[[0, 4]]
    k_lines[0] = pd.to_datetime(k_lines[0], unit='ms')
    k_lines[4] = k_lines[4].astype(float)
    k_lines = k_lines.rename(columns={0: 'time', 4: 'close'})
    result = pd.DataFrame()
    result['time'] = k_lines['time']
    for period in periods:
        rsi_values = calculate_rsi(k_lines['close'], period)
        result[f'RSI {period}'] = rsi_values
    return result

asset = "BTCUSDT"
periods = [14, 27, 100]
rsi_data = get_rsi_data(asset, periods)
print(rsi_data)
