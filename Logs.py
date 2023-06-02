import re
import datetime
import locale
from util import get_datetime_from_text

class Logs:
    def __init__(self):
        self.logs = {}
        self.current_logs = {}
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')


    def read_logs(self, path):
        self.logs.clear()

        with open(path, 'r') as file:
            for log in file:
                log.strip()
                try:
                    match = self.__get_regex_match(log)
                    details = self.__entry_to_dict(match)
                    self.logs[log] = details

                except Exception as e:
                    print(e)
        
        self.current_logs = self.logs


    def get_logs_datespan(self):
        details = list(self.current_logs.values())

        first_date = get_datetime_from_text(details[0]['date'])
        last_date = get_datetime_from_text(details[-1]['date'])

        return first_date, last_date
    

    def filter_logs(self, min_date, max_date):
        self.current_logs = {k : v for k, v in self.logs.items() 
                             if min_date <= get_datetime_from_text(v['date']) <= max_date}

    def reset_filtering(self):
        self.current_logs = self.logs


    def __entry_to_dict(self, match):
        ip, date, time, timezone, method, path, code, size = match.groups()

        date = datetime.datetime.strptime(date, '%d/%b/%Y').strftime(r'%Y-%m-%d')

        log_dict = {'ip': ip, 
                    'date': date,
                    'time': time,
                    'timezone': str(datetime.datetime.strptime(timezone, '%z').tzinfo),
                    'method': method,
                    'path': path,
                    'code': code,
                    'size': '-' if size == '-' else size + ' B'}
    
        return log_dict


    def __get_regex_match(self, log):
        log_regex1 = re.compile(r'^(\S+) \S+ \S+ \[(\d{2}/\w{3}/\d{4}):(\d{2}:\d{2}:\d{2}) ([-+]\d{4})\]'
                            r' "([A-Z]+ )?([^\s"]*)(?:\s+\S*){0,3}" (\d{3}) (\d+|-)$')
        log_regex2 = re.compile(r'^(\S+) \S+ \S+ \[(\d{2}/\w{3}/\d{4}):(\d{2}:\d{2}:\d{2}) ([-+]\d{4})\]'
                            r' "([A-Z]+ )?([^\s"]*)(?:\s+\S*)*" (\d{3}) (\d+)$')

        match1 = log_regex1.match(log)
        match2 = log_regex2.match(log)

        if match1:
            return match1
        if match2:
            return match2

        raise Exception('Incorrect log formatting: ' + log)