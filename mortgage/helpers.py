import calendar
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

DATE_MASK = '%Y-%m-%d'


def days_in_year(year: int) -> int:
    return 365 + calendar.isleap(year)


def get_last_day_in_months(date_to_calc: date) -> int:
    year, month = date_to_calc.year, date_to_calc.month
    return calendar.monthrange(year, month)[1]


def get_timedelta(months: int) -> relativedelta:
    return relativedelta(months=months)


def get_months_difference(date1: date, date2: date) -> int:
    time_diff = relativedelta(date1, date2)
    return time_diff.years * 12 + time_diff.months


def parse_date(date_char: str) -> date:
    return datetime.strptime(date_char, DATE_MASK).date()
