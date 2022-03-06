from datetime import date, datetime, timedelta


def date_now():
    return datetime.now()


def date_yday():
    return datetime.now() - timedelta(1)


def string_to_date(date: str):
    return datetime.fromisoformat(date)


def leap_year(year):
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    if year % 4 == 0:
        return True
    return False


def days_in_month(month, year):
    if month in {1, 3, 5, 7, 8, 10, 12}:
        return 31
    if month == 2:
        if leap_year(year):
            return 29
        return 28
    return 30


# from S.O.
def last_day_of_month(any_day):
    # this will never fail
    # get close to the end of the month for any day, and add 4 days 'over'
    next_month = any_day.replace(day=28) + timedelta(days=4)
    # subtract the number of remaining 'overage' days to get last day of current month, or said programattically said, the previous day of the first of next month
    return next_month - timedelta(days=next_month.day)


def calculate_premium(dob: str):
    age = __calculate_age(dob)
    return 600 + 0.3 * (abs(age - 50)) ** 1.5


def __calculate_age(dob: str):
    today = date.today()
    dob_as_date = string_to_date(dob)
    return today.year - dob_as_date.year - ((today.month, today.day) < (dob_as_date.month, dob_as_date.day))

