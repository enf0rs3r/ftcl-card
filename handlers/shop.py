import json
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram import Router
from aiogram.filters import Command

router = Router()

# Функция загрузки данных о паках
def load_packs():
    with open("data/packs.json", "r", encoding="utf-8") as file:
        return json.load(file)

packs = load_packs()  # Загружаем паки один раз при запуске

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

# Универсальная функция отправки информации о паке
async def send_pack_info(message: types.Message, pack_key: str, callback_data: str):
    pack = packs.get(pack_key)
    if not pack:
        await message.answer("Ошибка: данный пак не найден.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🎁 Открыть", callback_data=callback_data)]]
    )
    pack_image = FSInputFile(f"photo/{pack['image']}")  # Берем картинку из packs.json

    caption = (
        f"🎁 **{pack['name']}**\n"
        f"💰 Цена: {pack['price']} (сейчас бесплатно)\n"
        f"⏳ Интервал открытия: {pack['interval']} часов\n"
        f"🎲 Шансы:\n"
    )

    for rarity, chance in pack["chances"].items():
        caption += f"   {rarity.capitalize()} — {chance}%\n"

    await message.answer_photo(pack_image, caption=caption, reply_markup=keyboard)

# Обработчик обычного пака
@router.message(lambda message: message.text == "📦 Обычный пак")
async def show_normal_pack_info(message: types.Message):
    await send_pack_info(message, "normal_pack", "open_normal_pack")

# Обработчик бесконечного пака
@router.message(lambda message: message.text == "♾ Бесконечный пак")
async def show_endless_pack_info(message: types.Message):
    await send_pack_info(message, "endless_pack", "open_endless_pack")

# Обработчик кнопки "Открыть" для обычного пака
@router.callback_query(lambda c: c.data == "open_normal_pack")
async def open_normal_pack(callback: types.CallbackQuery):
    from handlers.open_pack import open_pack
    await open_pack(callback.message)  # Открываем обычный пак
    await callback.answer()

# Обработчик кнопки "Открыть" для бесконечного пака
@router.callback_query(lambda c: c.data == "open_endless_pack")
async def open_endless_pack(callback: types.CallbackQuery):
    from handlers.endless_pack import endless_pack
    await endless_pack(callback.message)  # Открываем бесконечный пак
    await callback.answer()
