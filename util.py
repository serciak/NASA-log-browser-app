import datetime

def get_datetime_from_text(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d')