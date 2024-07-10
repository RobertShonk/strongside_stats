import datetime

def seconds_to_mins(seconds):
    hours = seconds // 3600
    minutes = seconds // 60
    sec = seconds % 60

    if hours > 0:
        return f'{hours}h {minutes}m {sec}s'
    
    return f'{minutes}m {sec}s'


def epoch_to_date(epoch):
    return datetime.datetime.fromtimestamp(epoch/1000).strftime('%m-%d-%Y')