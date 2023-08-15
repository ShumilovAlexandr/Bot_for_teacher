from aiogram import executor
from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           CallbackQuery,
                           Message)
from aiogram.dispatcher import FSMContext


from teach_bot.loader import dp
from teach_bot.handlers.add_user import show_start_message
from teach_bot.handlers.cancel_lesson import select_lesson
from teach_bot.handlers.contact_teacher import write_message



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
            await show_start_message(callback.message, state=state)
        case "button2":
            await select_lesson(callback.message, state=state)
        case "button3":
            await write_message(callback.message, state=state)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)



# TODO
#    Надо сделать таску на автоматическое удаление записей на уроки,
#    которые уже были проведены (то есть, из бд каждый понедельник удалять
#    уроки на две недели назад).
#    Добавить отправку ученикам раз в неделю сообщения в чат,
#    чтобы не забывали записываться на занятия.
#    Также, сделать еще одну таску, чтобы учителю в конце рабочего дня в
#    20.00 приходило оповещение на почту с записями на урок на завтра.