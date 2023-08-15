from aiogram.dispatcher.filters.state import (State,
                                              StatesGroup)


# Используется для хранения состояния набора данных пользователя при записи
# на урок.
class LessonData(StatesGroup):
    date_lesson = State()
    time = State()
    name = State()

# Используется для хранения состояния набора данных пользователя при отмене
# забронированого урока.
class CancelLesson(StatesGroup):
    date_lsn = State()
    time_lsn = State()


# Используется для хранения состояния набора данных при связи с преподавателем.
class ContactTeacher(StatesGroup):
    text_message = State()
