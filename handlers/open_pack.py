import json
import random
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from database.db import add_card_to_collection, get_last_open_time, update_last_open_time
from datetime import datetime, timedelta

router = Router()

# Загружаем данные о паках
def load_packs():
    """Загружает список паков из packs.json"""
    with open("data/packs.json", "r", encoding="utf-8") as file:
        return json.load(file)  # Загружаем как список

packs = load_packs()
PACK_COOLDOWN = timedelta(hours=packs["normal_pack"]["interval"])  # 7 часов

def load_cards():
    """Загружает карточки из cards.json"""
    with open("data/cards.json", "r", encoding="utf-8") as file:
        return json.load(file)

def get_random_card():
    """Выбирает случайную карту с учетом шансов редкости"""
    cards = load_cards()
    rarity_chances = packs["normal_pack"]["chances"]

    rarity = random.choices(
        list(rarity_chances.keys()),
        weights=rarity_chances.values(),
        k=1
    )[0]

    filtered_cards = [card for card in cards if card["rarity"] == rarity]

    return random.choice(filtered_cards) if filtered_cards else None

@router.message(Command("open_pack"))
async def open_pack(message: Message):
    """Открытие обычного пака"""
    user_id = message.from_user.id
    last_open_time = get_last_open_time(user_id)

    if last_open_time:
        last_open_time = datetime.strptime(last_open_time, "%Y-%m-%d %H:%M:%S.%f")
        remaining_time = PACK_COOLDOWN - (datetime.now() - last_open_time)

        if remaining_time > timedelta(0):
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes = remainder // 60
            await message.answer(f"⌛ Вы недавно открывали пак. Подождите ещё {hours} ч {minutes} мин!")
            return

    card = get_random_card()

    if not card:
        await message.answer("Не удалось открыть пак, попробуйте позже.")
        return

    update_last_open_time(user_id)
    add_card_to_collection(user_id, card["card_id"])

    card_image = FSInputFile(f"photo/{card['card_id']}.jpg")
    caption = f"🎴 <b>{card['name']}</b>\n⭐ Редкость: {card['rarity'].capitalize()}\n🏆 ID карты: {card['card_id']}\n🔥 Рейтинг: {card['rating']}"

    await message.answer_photo(card_image, caption=caption)
