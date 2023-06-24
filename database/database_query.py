from .databases import get_connection


def check_records(date, time):
    """
    Функция нужна для проверки наличия загружаемых в таблицу БД записей.

    :param date: дата проведения урока
    :param time: время проведения урока.
    :return: возвращает True, если в таблице timesheet имеется запись,
    или False, если запись отсутствует
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS (SELECT 1 from timesheet where "
                f"record_date='{date}' and record_time='{time}')")
    table_check = cur.fetchone()[0]
    cur.close()
    conn.close()
    return table_check