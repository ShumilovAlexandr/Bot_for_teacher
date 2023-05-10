import psycopg2
import requests


def get_connection():
    """Функция подключения приложения к базе данных."""
    conn = None
    try:
        conn = psycopg2.connect(
                host='localhost',
                user='postgres',
                password='postgres',
                database='bot_teacher'
        )
    except OperationalError as e:
        print("Ошибка соединения")
    return conn

def create_table(table_name):
    """Функция создания таблицы."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE {table_name} ("
                "record_date DATE,"
                "record_time TIME,"
                "fio TEXT,"
                "USER_ID TEXT)")
    conn.commit()
    cur.close()
    conn.close()

def insert_into_table(date, time, fio, user_id):
    """
    Фунция для внесения информации в таблицу timesheet.

    :param date - дата проведения урока.
    :param time - время проведения урока.
    :param fio - имя и фамилия ученика.
    :param user_id - id ученика
    Функция ничего не возвращает, она отвечает за загрузку данных в таблицу
    в базу данных postgres.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Проверяем, есть ли такая таблица timesheet
    cur.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'timesheet'
        )
    """)
    table_exists = cur.fetchone()[0]
    # и если нет, то создаем
    if not table_exists:
        create_table('timesheet')
    # если есть, загружаем в нее данные нового ученика.
    else:
        cur.execute("INSERT into timesheet "
                    "(record_date,"
                    "record_time, "
                    "fio, user_id) values (%s, %s, %s, %s) ",
                    (date, time, fio, user_id))
        conn.commit()
        cur.close()
        conn.close()

# TODO эта функция должна проверить, есть ли записи в базе данных. Если
#  есть, то в бот выводится сообщение типа сорян, время занято. если время
#  свободно, то выводится другое сообщение и запись сохраняется в базе данных.
def check_records(date, time, fio, user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS (SELECT 1 from timesheet where record_date="
                f"{date} and record_time = {time}")
    table_check = cur.fetchall()
    if not table_check:
        insert_into_table(date, time, fio, user_id)
