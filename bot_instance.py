from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import TOKEN

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()  # Работает, но лучше передавать storage

# Альтернативный вариант с MemoryStorage (если нужно хранить состояния пользователей)
# from aiogram.fsm.storage.memory import MemoryStorage
# dp = Dispatcher(storage=MemoryStorage())
