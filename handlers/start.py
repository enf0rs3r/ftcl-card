# start.py
from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database.db import add_user  # Импортируем функцию add_user
from bot_instance import dp  # Импортируем диспетчер из bot_instance

# Инициализация роутера
router = Router()

# Главное меню
menu = ReplyKeyboardMarkup(
    keyboard=[ 
        [KeyboardButton(text="🏢 Магазин"), KeyboardButton(text="📅 Профиль")]
    ],
    resize_keyboard=True
)

# Обработчик команды /start
@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    # Добавляем пользователя в БД (если его еще нет)
    add_user(user_id, username)
    
    # Приветствие и главное меню
    await message.answer(
        "Привет! Ты попал в бота карточек ФТКЛ. Выбери действие:\n\nБот выполнен Энфорсером (@enfhub) и Педро (@mrazisyka). Будь добр, подпишись на наш канал - только там все свежие инсайды (@cardsftcl)",
        reply_markup=menu
    )

# Обработчик кнопки "Магазин"
@router.message(lambda message: message.text == "🏢 Магазин")
async def shop_handler(message: types.Message):
    await message.answer("Выберите, что хотите сделать в магазине:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎁 Паки"), KeyboardButton(text="⚒ Трейд")],
            [KeyboardButton(text="💳 Покупка карточек"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    ))

# Обработчик кнопки "Профиль"
@router.message(lambda message: message.text == "📅 Профиль")
async def profile_handler(message: types.Message):
    await message.answer("Ваш профиль:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Статистика"), KeyboardButton(text="🎴 Коллекция"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    ))

# Обработчик кнопки "Назад"
@router.message(lambda message: message.text == "🔙 Назад")
async def back_handler(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=menu)
