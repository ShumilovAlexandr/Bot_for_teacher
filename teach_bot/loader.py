import os

from aiogram import (Bot,
                     Dispatcher)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv


load_dotenv()

# Создание экземпляра бота
bot = Bot(os.getenv("TOKEN"))
# Объект диспетчера
dp = Dispatcher(bot, storage=MemoryStorage())