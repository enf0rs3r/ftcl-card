import json
import random
from aiogram import Router, F
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database.db import add_card_to_collection, get_last_open_time, update_last_open_time
from datetime import datetime, timedelta

router = Router()

# Загружаем данные паков
def load_packs():
    with open("data/packs.json", "r", encoding="utf-8") as file:
        return json.load(file)

packs = load_packs()
normal_pack = next(pack for pack in packs if pack["pack_id"] == "standard")

PACK_COOLDOWN = timedelta(hours=normal_pack["interval"])

# Загружаем карточки
def load_cards():
    with open("data/cards.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Генерация случайной карты
def get_random_card():
    cards = load_cards()
    rarity = random.choices(
        list(normal_pack["chances"].keys()),
        weights=normal_pack["chances"].values(),
        k=1
    )[0]
    filtered_cards = [card for card in cards if card["rarity"] == rarity]
    return random.choice(filtered_cards) if filtered_cards else None

# Обработчик информации о паке
@router.message(Command("open_pack"))
async def open_pack_info(message: Message):
    photo_path = f"photo/{normal_pack['photo']}"
    caption = (f"📦 <b>{normal_pack['name']}</b>\n"
               f"💰 Цена: {normal_pack['price']} монет\n"
               f"⏳ Интервал: {normal_pack['interval']} часов\n"
               f"🎲 Шансы:\n" +
               "\n".join([f"{rarity.capitalize()}: {chance}%" for rarity, chance in normal_pack["chances"].items()]))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🃏 Открыть пак", callback_data="open_normal_pack")]
    ])

    await message.answer_photo(FSInputFile(photo_path), caption=caption, reply_markup=keyboard)

# Обработчик открытия пака
@router.callback_query(F.data == "open_normal_pack")
async def open_normal_pack(callback_query):
    user_id = callback_query.from_user.id
    last_open_time = get_last_open_time(user_id)

    if last_open_time:
        last_open_time = datetime.strptime(last_open_time, "%Y-%m-%d %H:%M:%S.%f")
        remaining_time = PACK_COOLDOWN - (datetime.now() - last_open_time)
        if remaining_time > timedelta(0):
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes = remainder // 60
            await callback_query.message.answer(f"⌛ Подождите ещё {hours} ч {minutes} мин перед открытием пака!")
            return

    card = get_random_card()
    if not card:
        await callback_query.message.answer("Ошибка! Не удалось открыть пак.")
        return

    update_last_open_time(user_id)
    add_card_to_collection(user_id, card["card_id"])
    
    card_image = FSInputFile(f"photo/{card['card_id']}.jpg")
    caption = f"🎴 <b>{card['name']}</b>\n⭐ Редкость: {card['rarity'].capitalize()}\n🏆 ID карты: {card['card_id']}\n🔥 Рейтинг: {card['rating']}"
    
    await callback_query.message.answer_photo(card_image, caption=caption)
