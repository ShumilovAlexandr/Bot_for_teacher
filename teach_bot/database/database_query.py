from .databases import get_connection


def establish_connection():
    conn = get_connection()
    cur = conn.cursor()
    return cur

def check_records(date):
    """
    Функция выводит записи из базы данных, а именно время для
    конкретной даты.

    :param date: дата проведения урока (тип данных - datetime.date)
    :return: список доступных временных слотов
    """
    cur = establish_connection()
    cur.execute(f"SELECT lesson_time FROM timelist WHERE lesson_time NOT IN "
                f"(SELECT record_time FROM timesheet WHERE "
                f"record_date = '{date}') ORDER BY lesson_time")
    available_times = [str(row[0]) for row in cur.fetchall()]
    cur.close()
    return available_times
