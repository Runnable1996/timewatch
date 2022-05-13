from time import sleep
import requests
from bs4 import BeautifulSoup as BS
from collections import defaultdict
from datetime import datetime
from functools import wraps

SITE = "https://c.timewatch.co.il"
GET_WORKING_DAYS_PATH = "punch/editwh.php"
VALIDATE_PATH = "punch/editwh2.php"
EDITPATH = "punch/editwh3.php"
LOGINPATH = "user/validate_user.php"

def BeautifulSoup(t):
    return BS(t, 'html.parser')

class ReconnectException(Exception):
    ...

class TimeWatch:

    def __init__(self, company_id: str, user:str, password:str):
        self.session = requests.Session()
        self.company = company_id
        self.user = user
        self.password = password

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, type, value, tb):
        self.session.close()

    def login_and_retry(method,retries = 4):
        @wraps(method)
        def wrapper(self, *method_args, **method_kwargs):
            for _ in range(retries):
                try:
                    return method(self, *method_args, **method_kwargs)
                except ReconnectException:
                    self.login()
            else:
                return method(self, *method_args, **method_kwargs)
        return wrapper

    def login(self) -> bool:
        r = self.session.post(f'{SITE}/{LOGINPATH}', {'comp': self.company, 'name': self.user, 'pw': self.password})
        parsed_login = BeautifulSoup(r.text)
        if not all(field in r.text for field in ["עדכון נתוני נוכחות"]):
            return False
        self.employeeid = int(parsed_login.find('input', id='ixemplee').get('value'))
        if self.employeeid:
            return True
        return False

    def update_shift_time(self, date: datetime, start :str, end : str) -> bool:
        date_str = f'{date.year}-{date.month}-{date.day}'
        start_hour, start_minute = self.time_to_tuple(start)
        end_hour, end_minute =  self.time_to_tuple(end)
        shift_data = {'d':date_str, 'emm0': str(start_minute), 'ehh0': str(start_hour),'xmm0': str(end_minute), 'xhh0': str(end_hour)}
        
        basic_data = self._create_basic_data(date)
        headers = {
          'Content-Type': "application/x-www-form-urlencoded",
          'Referer': f"{SITE}{GET_WORKING_DAYS_PATH}?ee={self.employeeid}&e={self.company}&m={date.month}&y={date.year}"
            }

        r = self.session.post(f'{SITE}/{EDITPATH}', data=self._prepare_data({**basic_data,**shift_data}), headers=headers)
        if "TimeWatch - Reject" in r.text or "error" in r.text or 'limited punch' in r.text:
            return False
        return True

    def get_working_dates(self, year:str, month:str) -> dict[str,list]:
        data = {'ee': self.employeeid, 'e': self.company, 'y': year, 'm': month}
        r = self.session.get(f'{SITE}/{GET_WORKING_DAYS_PATH}', params=data)
        date_durations = defaultdict(lambda:list())
        for tr in BeautifulSoup(r.text).findAll('tr',{"class":"update-data"}):
            tds = tr.findAll('td')
            date = datetime.strptime(tds[0].getText().split(" ")[0], "%d-%m-%Y").date()
            cause = True if self.clean_text(tds[10].getText()) else False
            working_day = True if self.clean_text(tds[3].getText()) else False
            if cause is False and working_day is True:
                date_durations[date].append(all(tds[12].getText() != missing for missing in ['חסרה כניסה/יציאה','חסרה יציאה','חסרה כניסה'])) # check if shift already field
                date_durations[date].append(tds[3].getText()) # get expected working hours
        return date_durations
      
    @login_and_retry
    def _create_basic_data(self, date:datetime) -> None:
        #assuming we need to reconnect when we have redirection at this page 
        if self.session.get(f"{SITE}/{GET_WORKING_DAYS_PATH}", params = {'ee': self.employeeid, 'e': self.company, 'y': date.year, 'm': date.month},allow_redirects=False).status_code != 200:
            raise ReconnectException

        r = self.session.get(f"{SITE}/{VALIDATE_PATH}",params = {"ie":self.company,"e":self.employeeid,"d":f"{date.year}-{date.month}-{date.day}","tl":self.employeeid})
        parsed_data = BeautifulSoup(r.text)
        data = {
            "e" : str(self.employeeid),
            "tl" : str(self.employeeid),
            "c" : self.company,
            "atypehidden" : parsed_data.find("input",{"name":"atypehidden"}).get('value'),
            "inclcontracts" : parsed_data.find("input",{"name":"inclcontracts"}).get('value'),
            "job" : parsed_data.find("input",{"name":"job"}).get('value'),
            "allowabsence" : parsed_data.find("input",{"name":"allowabsence"}).get('value'),
            "allowremarks" : parsed_data.find("input",{"name":"allowremarks"}).get('value'),
            "csrf_token" : parsed_data.find("input",{"name":"csrf_token"}).get('value'),
            'task0': '0',
            'taskdescr0': '',
            'what0': '1',
            "excuse":'0'          
        }

        return data

    def validate_shift_time(self,date : datetime) -> bool:
        r = self.session.get(f"{SITE}/{VALIDATE_PATH}",params = {"ie":self.company,"e":self.employeeid,"d":f"{date.year}-{date.month}-{date.day}","tl":self.employeeid})
        parsed_data = BeautifulSoup(r.text)
        return parsed_data.find("input",id="emm0").get('value') and parsed_data.find("input",id="ehh0").get('value') and parsed_data.find("input",id="xmm0").get('value') and parsed_data.find("input",id="xhh0").get('value')

    @staticmethod
    def _prepare_data(data:dict) -> str:
        return '&'.join(f'{key}={value}' for key,value in data.items())

    @staticmethod
    def time_to_tuple(t: str) -> tuple[str,str]:
        t = TimeWatch.clean_text(t)
        if ':' in t:
            t = tuple(t.split(':'))
        else:
            t = ('', '')
        return t

    @staticmethod
    def clean_text(text :str ) -> str:
        return text.strip().replace("&nbsp;", "")