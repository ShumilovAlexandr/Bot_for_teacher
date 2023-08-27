import smtplib
import os
import datetime
import asyncio

from datetime import timedelta
from celery import Celery
from email.message import EmailMessage
from dotenv import load_dotenv
from sqlalchemy import select
from celery.schedules import crontab
from aiogram.types import Message


from teach_bot.database.databases import session
from teach_bot.database.tables import Timesheet
from ..loader import (bot,
                      dp)

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SENDER")
SMTP_PASSWORD = os.getenv("EMAIL_PASSWORD")

app = Celery('tasks', broker="redis://localhost:6379")


def get_data_from_tables():
    """Выборка расписания на завтра для учителя."""
    now = datetime.datetime.now().date() + timedelta(days=1)
    stmt = select(Timesheet.fio,
                  Timesheet.record_date,
                  Timesheet.record_time).\
        where(Timesheet.record_date == now)
    result = session.execute(stmt)
    return result.fetchall()


def get_email_text(data):
    """Тут параметры для отправки."""
    email = EmailMessage()
    email["Subject"] = "Расписание на завтра."
    email["From"] = SMTP_USER
    email["To"] = SMTP_USER

    email.set_content(
       "Вот твои уроки на завтра: \n\n" + "\n".join([f"{row.fio} "
                                                     f"{row.record_date} "
                                                     f"{row.record_time} "
                                                     for row in data])
    )
    return email


@app.task
def send_email_report():
    """
    Сама таска, которая отвечает за отправку расписания на почту
    преподавателю.
    """
    sender = SMTP_USER
    password = SMTP_PASSWORD
    data = get_data_from_tables()

    server = smtplib.SMTP(SMTP_HOST, int(SMTP_PORT))
    try:
        server.starttls()
        server.login(sender, password)
        email = get_email_text(data)
        server.sendmail(sender, sender, email.as_string())
        return 'Сообщение доставлено'
    except smtplib.SMTPException as ex:
        print(f"{ex} Проверь логин и пароль!")


async def send_reminder(user_chat_id):
    """
    Функция отправляет всем учащимся напоминание, чтобы не забывали
    заниматься и бронировали время урока.
    """
    await bot.send_message(chat_id=user_chat_id,
                           text="Продуктивной рабочей недели всем! Не забываем "
                                "записываться на урок, пока другие Вас не "
                                "опередили 😉😉😉")

@app.task
def send_weekly_reminder():
    """
    Выборка из таблицы всех id чатов учащихся, удаляем дубляжи (чтобы не
    отправлять одному и тому же ученику много сообщений), и вызываем
    функцию отправки сообщения.
    """
    stmt = session.query(Timesheet.chat_id)
    users = session.execute(stmt).fetchall()
    for user in set(users):
        print(user)
        user_chat_id = user[0]
        asyncio.run(send_reminder(user_chat_id))


# Запуск таск
app.conf.beat_schedule = {
    "run-task-every-day": {
        "task": "teach_bot.utils.tasks.send_email_report",
        "schedule": crontab(hour=20, minute=0)
    },
    "run-task-every-monday": {
        "task": "teach_bot.utils.tasks.send_weekly_reminder",
        "schedule": crontab(day_of_week="mon", hour=12, minute=0)
    }
}
app.conf.timezone = "Europe/Moscow"