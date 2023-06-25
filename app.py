import datetime
import os
import json

from aiogram import (Bot,
                     Dispatcher,
                     executor)
from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           CallbackQuery,
                           Message)
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy import insert
from dotenv import load_dotenv

from database.databases import Session
from utils.validators import (check_time_range,
                              check_time_format,
                              check_date_format,
                              check_date_range)
from database.tables import Timesheet
from database.database_query import check_records
from utils.states import (LessonData,
                           CancelLesson)


load_dotenv()

# Создание экземпляра бота
bot = Bot(os.getenv("TOKEN"))
# Объект диспетчера
dp = Dispatcher(bot, storage=MemoryStorage())

session = Session()


@dp.message_handler(commands=['start'])
async def start(message: Message):
    """Стартовая страница бота.

    Здесь предлагается на выбор 3 действия (3 кнопки):
    записаться на урок, отменить запланированный урок, и связаться с учителем.
    send_message - стартовое приветствие.
    reply_markup - "привязывает" клавиатуру к стартовой странице.
    """
    button1 = InlineKeyboardButton(text="Записаться на урок к учителю 🇬🇧",
                                   callback_data='button1')
    button2 = InlineKeyboardButton(text="Отменить запланированный урок ❌",
                                   callback_data='button2')
    button3 = InlineKeyboardButton(text="Связаться с преподавателем 💻",
                                   callback_data='button3')
    markup = InlineKeyboardMarkup(row_width=1).add(button1, button2, button3)
    await message.answer("Привет 👋 Твое изучение английского языка уже "
                         "началось! Выбери интересующее тебя действие.",
                         reply_markup=markup)


@dp.callback_query_handler(lambda callback: True)
async def check_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка результата нажатия той или иной кнопки."""
    match callback.data:
        case "button1":
            await check_date(callback.message, state=state)
        case "button2":
            await select_lesson(callback.message, state=state)
        case "button3":
            pass

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
    # Запускаем снова стартовый выбор кнопок.
    await start(message)

### Функционал отмены забронированного урока. ###
@dp.message_handler(text=["Отменить запланированный урок ❌"])
async def select_lesson(message: Message, state: FSMContext):
    """
    Функция, отвечающая за вывод дат, в которые настоящий
    пользователь забронировал себе уроки.
    """
    lesson = session\
        .query(Timesheet.record_date)\
        .filter(Timesheet.user_id == message.chat.id)\
        .all()

    # Необходимо отформатировать выводимую из БД информацию
    formatted_dates = [date[0].strftime('%Y-%m-%d') for date in lesson]
    markup = InlineKeyboardMarkup(row_width=1)

    # Создаем кнопки с датами.
    for less in formatted_dates:
        buttons = InlineKeyboardButton(text=str(less),
                                       callback_data = f'{less}')
        markup.add(buttons)

    # Сохраняем состояние действия пользователя.
    await state.set_state(CancelLesson.date_lsn)
    await bot.send_message(message.chat.id, "Жаль конечно \U0001F61E. "
                                            "Надеюсь, Вы просто решили "
                                            "перенести время. Выбери, в какой день "
                                            "Вы хотите отменить урок "
                                            "\U0001F4C5", reply_markup=markup)

@dp.callback_query_handler(lambda callback: True, state=CancelLesson.date_lsn)
async def select_time(callback: CallbackQuery, state: \
    FSMContext):
    """
    Функция, отвечающая за вывод времени применимо к дате, в которые настоящий
    пользователь забронировал себе уроки.
    """
    await state.update_data(date_lsn=callback.data)
    time_lesson = session \
        .query(Timesheet.record_time) \
        .filter(Timesheet.record_date == callback.data) \
        .all()
    markup = InlineKeyboardMarkup(row_width=1)

    formatted_times = [time[0].strftime("%H:%M") for time in time_lesson]
    # Создаем кнопки со временем на забронированные даты.
    for time in formatted_times:
        buttons = InlineKeyboardButton(text=str(time),
                                       callback_data=f'{time}')
        markup.add(buttons)

    # Сохраняем состояние действия пользователя.
    await state.set_state(CancelLesson.time_lsn)
    await callback.message.answer(text="Теперь, выберите время, "
                                       "на которое у Вас забронирован "
                                       f"урок",
                                  reply_markup=markup)




@dp.callback_query_handler(lambda callback: True, state=CancelLesson.time_lsn)
async def select_time(callback: CallbackQuery, state: \
                      FSMContext):
    """
    Функция, отвечающая за удаление урока из базы данных.
    """
    await state.update_data(time_lsn=callback.data)
    data = await  state.get_data()
    date = data['date_lsn']
    time = data['time_lsn']
    await callback.message.answer(text=f"Запись {date} на {time} отменена. "
                                       f"Будем рады Вас видеть у меня на "
                                       f"занятии! Возвращайтесь😍😍😍")
    stmt = session\
        .query(Timesheet) \
        .filter(Timesheet.record_date == date)\
        .filter(Timesheet.record_time == time)\
        .delete()
    session.commit()
    # Сбрасываем состояние отмены урока.
    await state.reset_state()


# TODO добавить кнопку, чтобы после завершения отмены урока, снова выводить
#  стартовое сообщение и набор кнопок.
# TODO Добавить теперь проверку, что если нет забронированных уроков,
#  при попытке отмены - выводить сообщение, что Вами не забронирован не один
#  урок.
# TODO также, разобраться, почему долго светятся кнопки.
# TODO и еще, проверку, чтобы не записываться больше чем на месяц вперед.


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

