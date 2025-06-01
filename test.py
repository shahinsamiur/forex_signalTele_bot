from tvDatafeed import TvDatafeed, Interval
from decimal import Decimal
from fivemintime import get_5min_candle_count
from read_json import readjson
from update_json import update_json

# Login (using no-login mode)
tv = TvDatafeed()

# Get candle counts and data
fiveminCandleSIze = get_5min_candle_count()
h4_data = tv.get_hist(symbol='EURUSD', exchange='OANDA', interval=Interval.in_4_hour, n_bars=2)
m5_data = tv.get_hist(symbol='EURUSD', exchange='OANDA', interval=Interval.in_5_minute, n_bars=fiveminCandleSIze)

# Loop through m5 candles
for i in range(1, len(m5_data)):  # Start from 1 to avoid negative index
    row = m5_data.iloc[i]
    prev_row = m5_data.iloc[i - 1]
    json = readjson()

    # Convert values from json to Decimal safely
    json_high = Decimal(json["high"]) if json["high"] != "" else Decimal("0")
    json_low = Decimal(json["low"]) if json["low"] != "" else Decimal("999999")
    row_high = Decimal(str(row['high']))
    row_low = Decimal(str(row['low']))

    # Bullish candle
    if row['open'] < row['close']:
        if (not json["isCrossed"] and h4_data["high"].iloc[0] < row['high']) or \
           (json["isCrossed"] and json_high < row_high):
            
            # Search for last sell candle
            for j in range(i, 1, -1):
                red_candle = m5_data.iloc[j]
                prev = m5_data.iloc[j - 1]

                if red_candle['open'] > red_candle['close'] and \
                   (prev['high'] < red_candle['high'] or prev['low'] > red_candle['low']):
                    update_json({"lastSellCandle": str(red_candle['close'])})
                    print(row['close'], red_candle.name ,"BUY")
                    break

            update_json({"high": str(row['high'])})
            if not json["isCrossed"]:
                update_json({"isCrossed": True})

    # Bearish candle
    if row['open'] > row['close']:
        if (not json["isCrossed"] and h4_data["low"].iloc[0] > row['low']) or \
           (json["isCrossed"] and json_low > row_low):
            
            # Search for last buy candle
            for j in range(i, 1, -1):
                green_candle = m5_data.iloc[j]
                prev = m5_data.iloc[j - 1]

                if green_candle['open'] < green_candle['close'] and \
                   (prev['low'] > green_candle['low'] or prev['high'] < green_candle['high']):
                    update_json({"lastBuyCandle": str(green_candle['close'])})
                    print(row['close'], green_candle.name ,"SELL")
                    break

            update_json({"low": str(row['low'])})
            if not json["isCrossed"]:
                update_json({"isCrossed": True})
