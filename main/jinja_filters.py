from datetime import datetime

def date(timestamp):
    return datetime.fromtimestamp(timestamp/1000).strftime('%m-%d-%Y')


def game_length(time):
    minutes = time // 60
    seconds = time % 60
    return f'{minutes} m {seconds} s'