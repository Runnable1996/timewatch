from datetime import datetime
import logging
import os
from typing import Protocol
import typer
from timewatch.TimeWatch import TimeWatch
app = typer.Typer()

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

START_SHIFT_TIME = '09:00'

class WatchSystem(Protocol):
  def __enter__(self):
    return self
  def get_working_dates(year:str,month:str) -> dict[str,list]:
    ...
  def update_shift_time(date: datetime, start :str, end : str) -> bool:
    ...
  def validate_shift_time(date: datetime) -> bool:
    ...

def calc_ending_time(start_time : str, expected_working_time : str) -> str:
  return ':'.join([f'{int(i[0])+int(i[1])}' for i in zip(start_time.split(':'),expected_working_time.split(':'))])

def _update_shifts_for_month(watch_system:WatchSystem, month:str, year:str):
  with watch_system as ws:
    month_working_days : dict = ws.get_working_dates(year,month)
    for working_day_date,working_day_data in month_working_days.items():
      already_field,expected_working_hours = working_day_data
      if already_field :
        logger.info(f'{working_day_date} already have updated shift info,\r\n skipping...')
        continue
      start_shift = START_SHIFT_TIME
      end_shift = calc_ending_time(start_shift,expected_working_hours)
      if not ws.update_shift_time(working_day_date,start_shift,end_shift):
        logger.error(f'there was error to update {working_day_date} shift,\r\n skipping...')
        continue
      ws.validate_shift_time(working_day_date)
      logger.info(f'{working_day_date} was updated sucssefully')

@app.command()
def update_month(
  company_id: str = typer.Argument(...),
  id: str = typer.Argument(...),
  password: str = typer.Argument(...),
  month: str = typer.Option(datetime.today().month,'--month','-m'),
  year: str = typer.Option(datetime.today().year,'--year','-y')):
  tw: TimeWatch = TimeWatch(company_id, id, password)
  _update_shifts_for_month(tw,month,year)

if __name__ == "__main__":
  app()
  