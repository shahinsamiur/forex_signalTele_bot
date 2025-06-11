from read_json import readjson
from functions.callApi import call_api
import pandas as pd
from datetime import datetime, time, timezone

# Check if market is open (based on UTC time)
def is_forex_market_open():
    now = datetime.now(timezone.utc)
    weekday = now.weekday()  # Monday = 0, Sunday = 6
    if weekday == 5:  # Saturday
        return False
    if weekday == 6 and now.time() < time(22, 0):  # Sunday before 10 PM
        return False
    if weekday == 4 and now.time() >= time(22, 0):  # Friday after 10 PM
        return False
    return True

if not is_forex_market_open():
    print("Market closed. Skipping execution.")
    exit(0)

# URLs
UPDATE_URL = "https://bot-flas-server.onrender.com/update"
SENDMESSAGE_URL = "https://bot-flas-server.onrender.com/send-message"

# Fetch market data from API
response = call_api(url="https://bot-flas-server.onrender.com/market-data", method="GET")

h4_data_list, m5_data_list, jsons = response["h4"], response["m5"], response["data"]

# Convert lists to DataFrames
h4_data = pd.DataFrame(h4_data_list)
m5_data = pd.DataFrame(m5_data_list)

# Initialize high and low if empty
if jsons.get("high", "") == "":
    call_api(url=UPDATE_URL, method="POST", payload={"high": h4_data.iloc[0]["high"]})
if jsons.get("low", "") == "":
    call_api(url=UPDATE_URL, method="POST", payload={"low": h4_data.iloc[0]["low"]})

# Loop through m5 candles starting from index 1
for i in range(1, len(m5_data)):
    row = m5_data.iloc[i]
    prev_row = m5_data.iloc[i - 1]
    json = response["data"]

    # Trade trigger check
    if (
        json.get("sessionEligibleForOpenTrade", False)
        and json.get("lastOppositeCandle", "") != ""
        and json.get("isCrossed", False)
    ):
        if json["side"] == "buy" and json["lastOppositeCandle"] < row["close"]:
            call_api(url=UPDATE_URL, method="POST", payload={"sessionEligibleForOpenTrade": False})
            call_api(url=SENDMESSAGE_URL, method="POST", payload={'text': f"BUY>>>>>>>sl--{json.get('high')}"})
        elif json["side"] == "sell" and json["lastOppositeCandle"] > row["close"]:
            call_api(url=UPDATE_URL, method="POST", payload={"sessionEligibleForOpenTrade": False})
            call_api(url=SENDMESSAGE_URL, method="POST", payload={'text': f"SELL>>>>>>>sl--{json.get('high')}"})

    # Sell setup (bullish candle)
    if row["open"] < row["close"]:
        condition1 = not json.get("isCrossed", False) and h4_data.iloc[0]["high"] < row["high"]
        condition2 = json.get("isCrossed", False) and json.get("high", 0) < row["high"]
        if condition1 or condition2:
            for j in range(i, 1, -1):
                if (
                    m5_data.iloc[j]["open"] > m5_data.iloc[j]["close"]
                    and (
                        m5_data.iloc[j - 1]["high"] < m5_data.iloc[j]["high"]
                        or m5_data.iloc[j - 1]["low"] > m5_data.iloc[j]["low"]
                    )
                ):
                    call_api(url=UPDATE_URL, method="POST", payload={"lastOppositeCandle": m5_data.iloc[j]["close"]})
                    break
            call_api(url=UPDATE_URL, method="POST", payload={"high": row["high"]})
            if not json.get("isCrossed", False):
                call_api(url=UPDATE_URL, method="POST", payload={"isCrossed": True, "side": "sell"})

    # Buy setup (bearish candle)
    if row["open"] > row["close"]:
        condition1 = not json.get("isCrossed", False) and h4_data.iloc[0]["low"] > row["low"]
        condition2 = json.get("isCrossed", False) and json.get("low", float('inf')) > row["low"]
        if condition1 or condition2:
            for j in range(i, 1, -1):
                if (
                    m5_data.iloc[j]["open"] < m5_data.iloc[j]["close"]
                    and (
                        m5_data.iloc[j - 1]["high"] < m5_data.iloc[j]["high"]
                        or m5_data.iloc[j - 1]["low"] > m5_data.iloc[j]["low"]
                    )
                ):
                    call_api(url=UPDATE_URL, method="POST", payload={"lastOppositeCandle": m5_data.iloc[j]["close"]})
                    break
            call_api(url=UPDATE_URL, method="POST", payload={"low": row["low"]})
            if not json.get("isCrossed", False):
                call_api(url=UPDATE_URL, method="POST", payload={"isCrossed": True, "side": "buy"})
