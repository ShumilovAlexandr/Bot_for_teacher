from aiogram.types import (Message,
                           ReplyKeyboardRemove)
from aiogram.dispatcher import FSMContext

from teach_bot.loader import (dp,
                              bot)


### Функционал сброса состояния.
@dp.message_handler(text="/cancelled", state="*")
async def cancel_handler(message: Message, state: FSMContext):
    await state.reset_state()
    await message.answer("Отмена. Начните выбор нужного Вам действия заново.",
                         reply_markup=ReplyKeyboardRemove())
