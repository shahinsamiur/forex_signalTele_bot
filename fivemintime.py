from datetime import datetime

def get_5min_candle_count(candle_hours=[23, 3, 7, 11, 15, 18]):
    now = datetime.now()  # Local time
    current_hour = now.hour
    current_minute = now.minute
    current_total_minutes = current_hour * 60 + current_minute

    # Create a list of possible candle hours, handling wrap-around
    valid_hours = sorted(candle_hours + [h - 24 for h in candle_hours if h > current_hour])
    nearest_past_candle_hour = max([h for h in valid_hours if h <= current_hour])

    candle_total_minutes = (nearest_past_candle_hour % 24) * 60

    # Calculate time difference with wrap-around
    diff_minutes = current_total_minutes - candle_total_minutes
    if diff_minutes < 0:
        diff_minutes += 1440

    five_min_candles = diff_minutes // 5
    return five_min_candles

# Call and print result
print(get_5min_candle_count())
