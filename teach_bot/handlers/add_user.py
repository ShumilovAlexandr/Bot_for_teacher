import datetime
import json

from aiogram.dispatcher import FSMContext
from aiogram.types import (Message,
                           InlineKeyboardButton,
                           InlineKeyboardMarkup,
                           CallbackQuery)
from aiogram_calendar import (SimpleCalendar,
                              simple_cal_callback)
from sqlalchemy import (insert,
                        select)

from teach_bot.utils.states import LessonData
from ..loader import (dp,
                      bot)
from ..database.database_query import check_records
from ..database.databases import session
from ..database.tables import (Timesheet,
                               Timelist)


@dp.message_handler(text =["Записаться на урок к учителю 🇬🇧"])
async def show_start_message(message: Message, state: FSMContext):
    """Функция для вывода календаря."""
    await message.answer(text="Пожалуйста, выберите дату "
                              "предполагаемого урока в "
                              "\U0001F4C5",
                         reply_markup=await SimpleCalendar().start_calendar())
    await state.set_state(LessonData.date_lesson)


@dp.callback_query_handler(simple_cal_callback.filter(),
                           state=LessonData.date_lesson)
async def select_date(callback_query: CallbackQuery,
                      callback_data: dict,
                      state: FSMContext):
    """
    Функция, где пользователь после выбора даты сохраняет свой выбор в машине
    состояния. Также, тут предлагается на выбор время урока.
    """
    selected, date = await SimpleCalendar().process_selection(
        callback_query, callback_data)
    if selected:
        # Проверка корректности введенного времени
        # (выбранная дата не задним числом).
        da = callback_data["year"]+'-'+callback_data["month"]+'-'+callback_data["day"]
        res = datetime.datetime.strptime(da, '%Y-%m-%d')
        # Проверяем приведенную строку с датой относительно текущей даты.
        if str(res) <= str(datetime.datetime.now()):

            # Если выбрана дата "задним" числом или текущая, посылаем в чат
            # соответствующее сообщение и выводим снова клавиатуру.
            await bot.send_message(callback_query.message.chat.id,
                                   "Дату урока и время надо бронировать заблаговременно. "
                                   "Задним и сегодняшним числом это сделать "
                                   "не получится \U0000263A",
                                   reply_markup=await SimpleCalendar().start_calendar())
            return
        else:
            # Проверка наличия свободных временных слотов на выбранную дату.
            available_times = check_records(res.date())
            if not available_times:
                await bot.send_message(text="На выбранную дату нет "
                                              "свободных временных слотов. Выберите другую "
                                              "дату.",
                                       chat_id=callback_query.message.chat.id,
                                       reply_markup=await SimpleCalendar().start_calendar())
                return
            # Выводим кнопки с свободным временем.
            markup = InlineKeyboardMarkup()
            for time_slot in available_times:
                button = InlineKeyboardButton(text=time_slot,
                                              callback_data=f"{time_slot}")
                markup.add(button)
            await callback_query.\
                message.\
                answer("Окей, вы решили забронировать урок "
                       f"{date.strftime('%Y-%m-%d')}. Давайте теперь определимся "
                       "со временем \U000023F0", reply_markup=markup)
            await state.update_data(date_lesson=res)
            await state.set_state(LessonData.time)


@dp.callback_query_handler(state=LessonData.time)
async def select_time(callback_query: CallbackQuery, state: FSMContext):
    """
    Функция для выбора времени предполагаемого урока (без указания
    даты).
    """
    date = (await state.get_data())['date_lesson']
    first_name = callback_query.from_user.first_name
    second_name = callback_query.from_user.last_name

    # Финальное сообщение, подтвержающее бронь.
    await callback_query.message.answer(f"Итак, {first_name} {second_name}, Вы записались "
                           f"{date.date()} в {callback_query.data} на проведение "
                           "урока английского языка. Учитель свяжется с Вами заранее "
                           "до проведения урока. Успехов Вам! 🇬🇧 🇬🇧 🇬🇧")

    # Коллекция данных для сохранения в базу данных
    data = {
        'record_date': date.date(),
        'record_time': callback_query.data,
        'fio': first_name + " " + second_name,
        'user_id': callback_query.from_user.id
    }
    # Сохранение данных ученика в БД.
    stmt = insert(Timesheet).values(data)
    session.execute(stmt)
    session.commit()

    # Сбрасываем состояние выбора пользователем.
    await state.finish()
