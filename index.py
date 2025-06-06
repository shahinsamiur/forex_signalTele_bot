from read_json import readjson
from functions.callApi import call_api
import pandas as pd
# https://bot-flas-server.onrender.com
UPDATE_URL = "https://bot-flas-server.onrender.com/update"  # Update endpoint
SENDMESSAGE_URL="https://bot-flas-server.onrender.com/send-message"
# Fetch market data from API
response = call_api(url="https://bot-flas-server.onrender.com/market-data", method="GET")

h4_data_list, m5_data_list, jsons = response["h4"], response["m5"], response["data"]

# Convert lists to DataFrames
h4_data = pd.DataFrame(h4_data_list)
m5_data = pd.DataFrame(m5_data_list)



messageData = {'text': "BUY>>>>>>>sl--" + str(jsons.get("high")),}
call_api(url=SENDMESSAGE_URL, method="POST", payload=messageData)

# Initialize high and low if empty
if jsons.get("high", "") == "":
    dataForUpdate = {"high": h4_data.iloc[0]["high"]}
    call_api(url=UPDATE_URL, method="POST", payload=dataForUpdate)
if jsons.get("low", "") == "":
    dataForUpdate = {"low": h4_data.iloc[0]["low"]}
    call_api(url=UPDATE_URL, method="POST", payload=dataForUpdate)


# Loop through m5 candles starting from 1 to avoid index errors
for i in range(1, len(m5_data)):
    row = m5_data.iloc[i]
    prev_row = m5_data.iloc[i - 1]
    json = response["data"]

    # Check trade trigger condition
    if (
        json.get("sessionEligibleForOpenTrade", False)
        and json.get("lastOppositeCandle", "") != ""
        and json.get("isCrossed", False)
    ):
        if json["side"] == "buy" and json["lastOppositeCandle"] < row["close"]:
            dataForUpdate = {"sessionEligibleForOpenTrade": False}
            call_api(url=UPDATE_URL, method="POST", payload=dataForUpdate)
            payload = {
                'text': "BUY>>>>>>>sl--" + str(json.get("high")),
            }
            call_api(url=SENDMESSAGE_URL, method="POST", payload=dataForUpdate)
        elif json["side"] == "sell" and json["lastOppositeCandle"] > row["close"]:
            dataForUpdate = {"sessionEligibleForOpenTrade": False}
            call_api(url=UPDATE_URL, method="POST", payload=dataForUpdate)
            messageData = {
                'text': "Sell>>>>>>>sl--" + str(json.get("high")),
            }
            call_api(url=SENDMESSAGE_URL, method="POST", payload=messageData)

    # Detect sell setup (bullish candle)
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
                    dataForUpdate = {"lastOppositeCandle": m5_data.iloc[j]["close"]}
                    call_api(url=UPDATE_URL, method="POST", payload=dataForUpdate)
                    break

            dataForUpdate = {"high": row["high"]}
            call_api(url=UPDATE_URL, method="POST", payload=dataForUpdate)
            if not json.get("isCrossed", False):
                dataForUpdate = {"isCrossed": True, "side": "sell"}
                call_api(url=UPDATE_URL, method="POST", payload=dataForUpdate)

    # Detect buy setup (bearish candle)
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
                    dataForUpdate = {"lastOppositeCandle": m5_data.iloc[j]["close"]}
                    call_api(url=UPDATE_URL, method="POST", payload=dataForUpdate)
                    break

            dataForUpdate = {"low": row["low"]}
            call_api(url=UPDATE_URL, method="POST", payload=dataForUpdate)
            if not json.get("isCrossed", False):
                dataForUpdate = {"isCrossed": True, "side": "buy"}
                call_api(url=UPDATE_URL, method="POST", payload=dataForUpdate)
