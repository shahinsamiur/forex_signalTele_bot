from tvDatafeed import TvDatafeed, Interval

from fivemintime import get_5min_candle_count
from fivemintime import get_5min_candle_count
from read_json import readjson
from update_json import update_json
# Interval.in_5_minute

# Interval.in_4_hour


# username = 'shahinsamiur647'
# password = 'SrS.shahin1710@@'

# tv = TvDatafeed(username, password)
tv = TvDatafeed()

# index
# fiveminCandleSIze=get_5min_candle_count()
h4_data = tv.get_hist(symbol='EURUSD',exchange='OANDA',interval=Interval.in_4_hour,n_bars=2)
m5_data = tv.get_hist(symbol='EURUSD',exchange='OANDA',interval=Interval.in_5_minute,n_bars=50)


for i in range(1, len(m5_data)):  # Start from 1 to avoid negative index
    row = m5_data.iloc[i]
    prev_row = m5_data.iloc[i - 1]
    
    json = readjson()




    if row['open'] < row['close']: # for sell setup means if the upside swipe
        # checking here is setup complete for open trade
        if(json["isCrossed"] and (json["side"]=="buy" and json["lastOppositeCandle"]<row['close'])):
           print("BUY NOW")
        elif (json["isCrossed"] and (json["side"]=="buy" and json["lastOppositeCandle"]<row['close'])):
           print("SELL NOW") 
        
        
        
        if (json["isCrossed"]==False and h4_data["high"].iloc[0] <row['high']) or (json["isCrossed"]==True and json["high"]<row['high']):
            for j in range(i, 1, -1):

                    if m5_data.iloc[j]['open'] > m5_data.iloc[j]['close'] and (m5_data.iloc[j-1]['high'] < m5_data.iloc[j]['high'] or m5_data.iloc[j-1]['low'] > m5_data.iloc[j]['low']):
                      update_json({"lastOppositeCandle": m5_data.iloc[j]['close']})
                      print(row['close'],m5_data.iloc[j].name)
                      break



            update_json({"high": row['high']})
            if not json["isCrossed"]:
                update_json({"isCrossed": True,"side":"sell"})


    elif row['open'] > row['close']: # for Buy setup means if the Downside swipe
        if (json["isCrossed"]==False and h4_data["low"].iloc[0] >row['low']) or (json["isCrossed"]==True and json["low"]>row['low']):
            for j in range(i, 1, -1): # finding last opposite candle here bearish candle

                    if m5_data.iloc[j]['open'] < m5_data.iloc[j]['close'] and (m5_data.iloc[j-1]['high'] < m5_data.iloc[j]['high'] or m5_data.iloc[j-1]['low'] > m5_data.iloc[j]['low']):
                      update_json({"lastOppositeCandle": m5_data.iloc[j]['close']})
                      print(row['close'],m5_data.iloc[j].name)
                      break



            update_json({"low": row['low']})
            if not json["isCrossed"]:
                update_json({"isCrossed": True,"side":"buy"})
    



        


