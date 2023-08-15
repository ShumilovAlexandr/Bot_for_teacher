import os

from aiogram.types import (Message,
                           ReplyKeyboardRemove)
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv

from ..loader import (dp,
                      bot)
from ..utils.states import ContactTeacher

load_dotenv()


### Функционал отправки сообщения учителю для связи.
@dp.message_handler(text="Связаться с преподавателем 💻")
async def write_message(message: Message, state: FSMContext):
    await message.answer("✍ Пожалуйста, укажите, по какому вопросу Вы хотите "
                         "связаться с учителем. Можно вкратце, парой слов 😉")
    await state.set_state(ContactTeacher.text_message)


@dp.message_handler(state=ContactTeacher.text_message)
async def send_message(message: Message, state: FSMContext):
    await message.answer("📲 Спасибо за заявку. Учитель свяжется с Вами в "
                         "Telegram в ближайшее время. Хорошего дня! 📲")
    await bot.send_message(os.getenv("TEACHER_ID"),
                           text=f"Пользователь с "
                                f"логином @{message.from_user.username} "
                                f"хочет с Вами связаться. Вот его сообщение: {message.text}")
    await state.reset_state()
