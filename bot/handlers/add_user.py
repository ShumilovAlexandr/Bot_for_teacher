import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           CallbackQuery,
                           Message)
from sqlalchemy import insert

from bot.utils.states import LessonData
from ..loader import (dp,
                      bot)
from ..utils.validators import (check_time_range,
                                check_time_format,
                                check_date_format,
                                check_date_range)
from ..database.database_query import check_records
from ..database.databases import session
from ..database.tables import Timesheet


### Функционал бронирования времени урока. ###
@dp.message_handler(text =["Записаться на урок к учителю 🇬🇧"])
async def check_date(message: Message, state: FSMContext):
    """
    Функция для указания даты предполагаемого урока (без указания
    времени).
    """
    await state.set_state(LessonData.date)
    await bot.send_message(message.chat.id, "Пожалуйста, введите дату "
                                            "предполагаемого урока в "
                                            "формате год-месяц-день "
                                            "(например, 2020-02-22) "
                                            "\U0001F4C5")

@dp.message_handler(state=LessonData.date)
async def check_time(message: Message, state: FSMContext):
    """
    Функция для указания времени предполагаемого урока (без указания
    даты).
    """
    await state.update_data(date=message.text)
    date_str = (await state.get_data())['date']
    # Проверяем, что дата введена в нужном формате
    if not check_date_format(date_str):
        await bot.send_message(message.chat.id, "\U00002757 Неверный формат "
                                                "даты. Дата урока должна указываться "
                                                "в формате год-месяц-день ("
                                                "цифрами) \U00002757")
        return
    # ... и в нужном диапазоне
    if not check_date_range(date_str):
        await bot.send_message(message.chat.id, "Задана несуществующая дата, или в сообщении "
                                                "ошибка. Попробуй еще раз "
                                                "\U0001F60C")
        return
    # ... и естественно заранее
    if date_str <= str(datetime.datetime.now()):
        await bot.send_message(message.chat.id, "Дату урока и время надо "
                                                "бронировать "
                                                "заблаговременно. Задним "
                                                "и сегодняшним числом это "
                                                "сделать не получится "
                                                "\U0000263A")
        return
    # Если дата введена правильно, то...
    await state.set_state(LessonData.time)
    await bot.send_message(message.chat.id, "Теперь укажите, во сколько будет "
                                            "проведен Ваш урок по МСК "
                                            "(например, 14:00) \U000023F0")

@dp.message_handler(state=LessonData.time)
async def check_name(message: Message, state: FSMContext):
    """Функция для указания имени ученика."""
    await state.update_data(time=message.text)
    date_str = (await state.get_data())['date']
    time_str = (await state.get_data())['time']

    # Проверяем, что время введено в нужно формате
    if not check_time_format(time_str):
        await bot.send_message(message.chat.id, "\U00002757 Неверный "
                                                "формат времени. Введите "
                                                "время в формате "
                                                "'чч:мм' \U00002757")
        return

    # ... и в нужном диапазоне
    if not check_time_range(time_str):
        await bot.send_message(message.chat.id, "Время должно быть в интервале "
                                                "между 10:00 и 20:00 с шагом в 1 час. "
                                                "Преподавателю тоже нужен "
                                                "отдых \U0001F60C")
        return

    # Проверка, что выбранное время и дата еще не заняты
    if check_records(date_str, time_str):
        await bot.send_message(message.chat.id,
                               f"Извините, но время {time_str} "
                               f"\U000023F0 на {date_str} \U0001F4C5 "
                               f"уже занято. "
                               f"Пожалуйста, выберите другое время.")
        return

    # Если вводимое время прошло проверку на формат и на диапазон, задаем
    # последний вопрос
    await state.set_state(LessonData.name)
    await bot.send_message(message.chat.id, "И последний вопрос - как к Вам "
                                            "можно обращаться? Желательно, "
                                            "если укажите имя и фамилию "
                                            "\U0001F609")

@dp.message_handler(state=LessonData.name)
async def show_result(message: Message, state: FSMContext):
    """
    Функция выводит результирующее сообщение и сохраняет ученика в базу
    данных.
    """
    await state.update_data(name=message.text)
    date = (await state.get_data())['date']
    time = (await state.get_data())['time']
    name = (await state.get_data())['name']

    # Финальное сообщение, подтвержающее бронь.
    await bot.send_message(message.chat.id,
                           f"Итак, {name}, Вы записались "
                           f"{date} на {time} на проведение "
                           f"урока английского языка. Учитель свяжется с "
                           f"Вами заранее до проведения урока. Успехов Вам! "
                           f"🇬🇧 🇬🇧 🇬🇧")
    # Коллекция данных для сохранения в базу данных
    data = {
        'record_date': date,
        'record_time': time,
        'fio': name,
        'user_id': message.from_user.id
    }
    # Сохранение данных ученика в БД.
    stmt = insert(Timesheet).values(data)
    session.execute(stmt)
    session.commit()

    # Сбрасываем состояние выбора пользователем.
    await state.reset_state()
