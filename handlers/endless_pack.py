import json
import random
from aiogram import Router, F
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database.db import add_card_to_collection

router = Router()

# Загружаем данные паков
def load_packs():
    with open("data/packs.json", "r", encoding="utf-8") as file:
        return json.load(file)

packs = load_packs()
endless_pack = next(pack for pack in packs if pack["pack_id"] == "endless")

# Загружаем карточки
def load_cards():
    with open("data/cards.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Выбор карты только с "common" редкостью
def get_common_card():
    cards = load_cards()
    common_cards = [card for card in cards if card["rarity"] == "common"]
    return random.choice(common_cards) if common_cards else None

# Обработчик информации о паке
@router.message(Command("endless_pack"))
async def endless_pack_info(message: Message):
    photo_path = f"photo/{endless_pack['photo']}"
    caption = (f"♾ <b>{endless_pack['name']}</b>\n"
               f"💰 Цена: {endless_pack['price']} монет\n"
               f"⏳ Интервал: {endless_pack['interval']} часов\n"
               f"🎲 Шансы:\n" +
               "\n".join([f"{rarity.capitalize()}: {chance}%" for rarity, chance in endless_pack["chances"].items()]))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🃏 Открыть пак", callback_data="open_endless_pack")]
    ])

    await message.answer_photo(FSInputFile(photo_path), caption=caption, reply_markup=keyboard)

# Обработчик открытия бесконечного пака
@router.callback_query(F.data == "open_endless_pack")
async def open_endless_pack(callback_query):
    user_id = callback_query.from_user.id
    card = get_common_card()

    if not card:
        await callback_query.message.answer("Ошибка! Не удалось открыть пак.")
        return

    add_card_to_collection(user_id, card["card_id"])
    
    card_image = FSInputFile(f"photo/{card['card_id']}.jpg")
    caption = f"🎴 <b>{card['name']}</b>\n⭐ Редкость: {card['rarity'].capitalize()}\n🏆 ID карты: {card['card_id']}\n🔥 Рейтинг: {card['rating']}"
    
    await callback_query.message.answer_photo(card_image, caption=caption)
