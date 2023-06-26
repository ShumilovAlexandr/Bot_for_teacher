from aiogram import executor
from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           CallbackQuery,
                           Message)
from aiogram.dispatcher import FSMContext


from teach_bot.loader import dp
from teach_bot.handlers.add_user import check_date
from teach_bot.handlers.cancel_lesson import select_lesson



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





if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)


# TODO также, разобраться, почему долго светятся кнопки.
# TODO и еще, проверку, чтобы не записываться больше чем на месяц вперед.
# TODO надо организовать, чтобы на любом этапе, когда пользователь нажмет на
#  \start, происходил вызов базового меню, а не когда все это добро
#  отработает. Частично при регистрации сделал, но чет как то криво. Надо
#  пересмотреть.