from datetime import datetime, timedelta, timezone

# Get the current UTC time
utc_time = datetime.now(timezone.utc)

# Add 6 hours to get UTC+6 time
utc_plus_6_time = utc_time + timedelta(hours=6)

# Extract the hour
hour = utc_plus_6_time.hour

print(hour)