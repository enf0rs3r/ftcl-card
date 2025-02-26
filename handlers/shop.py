from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router
from handlers.open_pack import open_pack_info
from handlers.endless_pack import endless_pack_info
from handlers.trade import start_trade
from database.db import export_user_cards
from aiogram.filters import Command

router = Router()

# Обработчик кнопки "🏢 Магазин"
@router.message(lambda message: message.text == "🏢 Магазин")
async def shop_handler(message: types.Message):
    await message.answer("Выберите, что хотите сделать в магазине:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎁 Паки"), KeyboardButton(text="⚒ Трейд")],
            [KeyboardButton(text="💳 Покупка карточек"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    ))

# Обработчик кнопки "🎁 Паки"
@router.message(lambda message: message.text == "🎁 Паки")
async def packs_handler(message: types.Message):
    await message.answer("Выберите тип пака:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Обычный пак"), KeyboardButton(text="♾ Бесконечный пак")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    ))

# Обработчик обычного пака (отправляет инфо о паке)
@router.message(lambda message: message.text == "📦 Обычный пак")
async def open_normal_pack_info(message: types.Message):
    await open_pack_info(message)  # Показывает описание пака и кнопку "Открыть"

# Обработчик бесконечного пака (отправляет инфо о паке)
@router.message(lambda message: message.text == "♾ Бесконечный пак")
async def open_endless_pack_info(message: types.Message):
    await endless_pack_info(message)  # Показывает описание пака и кнопку "Открыть"

# Обработчик кнопки "Трейд"
@router.message(lambda message: message.text == "⚒ Трейд")
async def trade_handler(message: types.Message):
    await message.answer("Используйте команду: /trade @username card1_id card2_id для обмена картами.")

# Обработчик кнопки "Покупка карточек"
@router.message(lambda message: message.text == "💳 Покупка карточек")
async def buy_handler(message: types.Message):
    await message.answer("Покупка карточек ещё не реализована.")  # Заглушка

@router.message(Command("export_cards"))
async def export_cards_handler(message: types.Message):
    file_path = export_user_cards()
    await message.answer_document(types.FSInputFile(file_path), caption="📄 Список карточек всех пользователей.")

# Обработчик кнопки "Назад"
@router.message(lambda message: message.text == "🔙 Назад")
async def back_handler(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏢 Магазин"), KeyboardButton(text="📅 Профиль")]],
        resize_keyboard=True
    ))
