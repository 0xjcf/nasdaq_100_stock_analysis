import datetime
import pytz

def get_next_friday_market_close():
    now = datetime.datetime.now(pytz.timezone('US/Eastern'))
    days_until_friday = (4 - now.weekday()) % 7
    if days_until_friday == 0 and now.time() >= datetime.time(16, 0):
        days_until_friday = 7
    next_friday = now + datetime.timedelta(days=days_until_friday)
    market_close_expiration = next_friday.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_close_expiration.timestamp()
