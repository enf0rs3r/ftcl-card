import json
import random
import asyncio
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, CallbackQuery
from database.db import add_card_to_collection
from datetime import datetime, timedelta

router = Router()
user_timestamps = {}  # Словарь для хранения времени последнего открытия пака

# Загружаем данные о паках
def load_packs():
    with open("data/packs.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Загружаем данные о картах
def load_cards():
    with open("data/cards.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Функция для выбора карты в зависимости от шансов
def get_random_card():
    cards = load_cards()
    
    rarity_chances = {
        "common": 90,
        "rare": 7,
        "epic": 3
    }

    chosen_rarity = random.choices(
        list(rarity_chances.keys()), 
        weights=rarity_chances.values(), 
        k=1
    )[0]

    filtered_cards = [card for card in cards if card["rarity"] == chosen_rarity]
    return random.choice(filtered_cards) if filtered_cards else None

# Обработчик для показа информации о бесконечном паке
@router.message(lambda message: message.text == "♾ Бесконечный пак")
async def endless_pack_info(message: types.Message):
    packs = load_packs()
    endless_pack = next((p for p in packs if p["pack_id"] == "endless"), None)

    if not endless_pack:
        await message.answer("Ошибка: информация о паке не найдена.")
        return

    photo = FSInputFile(f"photo/{endless_pack['photo']}")
    text = (f"📦 <b>{endless_pack['name']}</b>\n"
            f"💰 Цена: {endless_pack['price']} монет\n"
            f"⏳ Интервал: Нет ограничений\n"
            f"🎲 Шансы:\n"
            f"  - Обычный: 90%\n"
            f"  - Редкий: 7%\n"
            f"  - Эпический: 3%")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Открыть", callback_data="open_endless_pack")]
    ])

    await message.answer_photo(photo, caption=text, reply_markup=keyboard)

# Обработчик нажатия кнопки "Открыть" с защитой от спама
@router.callback_query(lambda c: c.data == "open_endless_pack")
async def open_endless_pack(call: CallbackQuery):
    user_id = call.from_user.id
    now = datetime.now()

    # Проверка на спам
    if user_id in user_timestamps and now - user_timestamps[user_id] < timedelta(seconds=1.5):
        await call.answer("⏳ Подождите перед открытием следующего пака!", show_alert=True)
        return

    user_timestamps[user_id] = now  # Обновляем время последнего открытия

    card = get_random_card()
    if not card:
        await call.message.answer("Не удалось открыть пак, попробуйте позже.")
        return

    add_card_to_collection(user_id, card["card_id"])

    card_image = FSInputFile(f"photo/{card['card_id']}.jpg")
    caption = (f"🎴 <b>{card['name']}</b>\n"
               f"⭐ Редкость: {card['rarity'].capitalize()}\n"
               f"🏆 ID карты: {card['card_id']}\n"
               f"🔥 Рейтинг: {card['rating']}")

    await call.message.answer_photo(card_image, caption=caption)
