from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           CallbackQuery,
                           Message)
from aiogram.dispatcher import FSMContext

from ..database.databases import session
from ..database.tables import Timesheet
from ..utils.states import CancelLesson
from ..loader import (dp,
                      bot)


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