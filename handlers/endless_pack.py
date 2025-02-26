import json
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CallbackQuery
from database.db import add_card_to_collection
import random

router = Router()

# Загружаем данные о паках
def load_packs():
    with open("data/packs.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Загружаем данные о картах
def load_cards():
    with open("data/cards.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Фильтруем карты только для бесконечного пака (только common)
def get_common_card():
    cards = load_cards()
    common_cards = [card for card in cards if card["rarity"] == "common"]
    return random.choice(common_cards) if common_cards else None

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
            + "\n".join([f"  - {rarity.capitalize()}: {chance}%" for rarity, chance in endless_pack["chances"].items()]))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Открыть", callback_data="open_endless_pack")]
    ])

    await message.answer_photo(photo, caption=text, reply_markup=keyboard)

# Обработчик нажатия кнопки "Открыть" для бесконечного пака
@router.callback_query(lambda c: c.data == "open_endless_pack")
async def open_endless_pack(call: CallbackQuery):
    user_id = call.from_user.id
    card = get_common_card()

    if not card:
        await call.message.answer("Не удалось открыть бесконечный пак, попробуйте позже.")
        return

    add_card_to_collection(user_id, card["card_id"])

    card_image = FSInputFile(f"photo/{card['card_id']}.jpg")
    caption = (f"🎴 <b>{card['name']}</b>\n"
               f"⭐ Редкость: {card['rarity'].capitalize()}\n"
               f"🏆 ID карты: {card['card_id']}\n"
               f"🔥 Рейтинг: {card['rating']}")

    await call.message.answer_photo(card_image, caption=caption)
