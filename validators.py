import datetime


def check_time_format(time_str):
    """Функция проверки корректности формата времени."""
    try:
        datetime.datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

def check_time_range(time_str):
    """Функция проверки корректности временного промежутка."""
    start_time = datetime.datetime.strptime('09:00', '%H:%M').time()
    end_time = datetime.datetime.strptime('19:00', '%H:%M').time()
    time = datetime.datetime.strptime(time_str, '%H:%M').time()
    if start_time < time <= end_time and time.minute == 0:
        return True
    return False

def check_date_format(date_str):
    """Функция проверки корректности формата даты."""
    try:
        datetime.date.fromisoformat(date_str)
        return True
    except ValueError:
        return False

def check_date_range(date_str):
    """
    Функция проверяет, что дата введена в существующем
    диапазоне значений.
    """
    date_format = "%Y-%m-%d"
    try:
        datetime.datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False
