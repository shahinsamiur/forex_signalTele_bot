# from tvDatafeed import TvDatafeed, Interval
# from fivemintime import get_5min_candle_count

from read_json import readjson
from update_json import update_json
from functions.callApi import call_api
import pandas as pd  # Added for DataFrame usage

# Fetch market data from API
data = call_api(url="https://bot-flas-server.onrender.com/market-data", method="GET")

# Convert h4 and m5 data to pandas DataFrames
h4_data = pd.DataFrame(data["h4"])
m5_data = pd.DataFrame(data["m5"])

print(h4_data)

# Initialize values if not already set in the JSON
jsons = readjson()
if jsons["high"] == "":
    update_json({"high": h4_data.iloc[0]["high"]})
if jsons["low"] == "":
    update_json({"low": h4_data.iloc[0]["low"]})

print(h4_data.iloc[0]["low"])

# Loop through m5 candles
for i in range(1, len(m5_data)):  # Start from 1 to avoid negative index
    row = m5_data.iloc[i]
    prev_row = m5_data.iloc[i - 1]
    json = readjson()

    # Check for trade trigger condition
    if (
        json.get("sessionEligibleForOpenTrade", False)
        and json.get("lastOppositeCandle", "") != ""
        and json["isCrossed"]
    ):
        print("lets check for trade")
        if json["side"] == "buy" and json["lastOppositeCandle"] < row["close"]:
            update_json({"sessionEligibleForOpenTrade": False})
        elif json["side"] == "sell" and json["lastOppositeCandle"] > row["close"]:
            update_json({"sessionEligibleForOpenTrade": False})

    # Detect sell setup (bullish candle)
    if row["open"] < row["close"]:
        if (not json["isCrossed"] and h4_data.iloc[0]["high"] < row["high"]) or (
            json["isCrossed"] and json["high"] < row["high"]
        ):
            for j in range(i, 1, -1):
                if (
                    m5_data.iloc[j]["open"] > m5_data.iloc[j]["close"]
                    and (
                        m5_data.iloc[j - 1]["high"] < m5_data.iloc[j]["high"]
                        or m5_data.iloc[j - 1]["low"] > m5_data.iloc[j]["low"]
                    )
                ):
                    update_json({"lastOppositeCandle": m5_data.iloc[j]["close"]})
                    break

            update_json({"high": row["high"]})
            if not json["isCrossed"]:
                update_json({"isCrossed": True, "side": "sell"})

    # Detect buy setup (bearish candle)
    if row["open"] > row["close"]:
        if (not json["isCrossed"] and h4_data.iloc[0]["low"] > row["low"]) or (
            json["isCrossed"] and json["low"] > row["low"]
        ):
            for j in range(i, 1, -1):
                if (
                    m5_data.iloc[j]["open"] < m5_data.iloc[j]["close"]
                    and (
                        m5_data.iloc[j - 1]["high"] < m5_data.iloc[j]["high"]
                        or m5_data.iloc[j - 1]["low"] > m5_data.iloc[j]["low"]
                    )
                ):
                    update_json({"lastOppositeCandle": m5_data.iloc[j]["close"]})
                    break

            update_json({"low": row["low"]})
            if not json["isCrossed"]:
                update_json({"isCrossed": True, "side": "buy"})
