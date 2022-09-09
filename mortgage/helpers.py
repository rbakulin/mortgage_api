import calendar

from dateutil import relativedelta


def days_in_year(year):
    return 365 + calendar.isleap(year)


def get_last_day_in_months(date):
    year, month = date.year, date.month
    return calendar.monthrange(year, month)[1]


def get_timedelta(months):
    return relativedelta.relativedelta(months=months)


def get_months_difference(date1, date2):
    time_diff = relativedelta.relativedelta(date1, date2)
    return time_diff.years * 12 + time_diff.months
