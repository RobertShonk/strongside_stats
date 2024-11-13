from datetime import datetime

def date(timestamp):
    return datetime.fromtimestamp(timestamp/1000)