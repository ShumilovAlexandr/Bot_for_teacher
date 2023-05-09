import datetime
import os

from aiogram import (Bot,
                     Dispatcher,
                     executor)
from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           CallbackQuery,
                           Message)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import (State,
                                              StatesGroup)
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dotenv import load_dotenv

from database.config import insert_into_table


load_dotenv()

# Создание экземпляра бота
bot = Bot(os.getenv("TOKEN"))
# Объект диспетчера
dp = Dispatcher(bot, storage=MemoryStorage())


# Используется для хранения состояния набора данных пользователя.
class LessonData(StatesGroup):
    date = State()
    time = State()
    name = State()


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
            pass
        case "button3":
            pass


# Функционал бронирования времени урока.
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
                                            "(например, 2020-02-22): ")

@dp.message_handler(state=LessonData.date)
async def check_time(message: Message, state: FSMContext):
    """
    Функция для указания времени предполагаемого урока (без указания
    даты).
    """
    await state.update_data(date=message.text)
    await state.set_state(LessonData.time)
    await bot.send_message(message.chat.id, "Теперь укажите, во сколько будет "
                                            "проведен Ваш урок по МСК "
                                            "(например, 14:00)")

@dp.message_handler(state=LessonData.time)
async def check_name(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(LessonData.name)
    await bot.send_message(message.chat.id, "И последний вопрос - как к Вам "
                                            "можно обращаться? Желательно, "
                                            "если укажите имя и фамилию "
                                            "\U0001F609")

@dp.message_handler(state=LessonData.name)
async def show_result(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    date = (await state.get_data())['date']
    time = (await state.get_data())['time']
    name = (await state.get_data())['name']
    await bot.send_message(message.chat.id, f"Итак, {name}, Вы записались "
                                            f"{date} на {time} на проведение "
                                            f"урока английского языка. Учитель свяжется с "
                                            f"Вами заранее до проведения урока. Успехов Вам! 🇬🇧 🇬🇧 🇬🇧")
    insert_into_table(date, time, name, message.from_user.id)



# TODO Функционал отмены запланированного занятия

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

