import json
import random
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from database.db import add_card_to_collection, get_last_open_time, update_last_open_time
from datetime import datetime, timedelta

router = Router()

# Шансы выпадения редкости
RARITY_CHANCES = {
    "common": 70,
    "rare": 17,
    "epic": 10,
    "legendary": 3
}

# Время ожидания между открытиями
PACK_COOLDOWN = timedelta(hours=10)

def load_cards():
    """Загружает карточки из cards.json"""
    with open("data/cards.json", "r", encoding="utf-8") as file:
        return json.load(file)

def get_random_card():
    """Выбирает случайную карту с учётом шансов редкости"""
    cards = load_cards()
    
    # Выбираем редкость по шансам
    rarity = random.choices(
        list(RARITY_CHANCES.keys()),
        weights=RARITY_CHANCES.values(),
        k=1
    )[0]
    
    # Фильтруем карточки по редкости
    filtered_cards = [card for card in cards if card["rarity"] == rarity]
    
    if not filtered_cards:
        return None  # Если вдруг карточек с такой редкостью нет
    
    return random.choice(filtered_cards)

@router.message(Command("open_pack"))
async def open_pack(message: Message):
    """Обработчик команды /open_pack"""
    user_id = message.from_user.id
    last_open_time = get_last_open_time(user_id)
    
    if last_open_time:
        last_open_time = datetime.strptime(last_open_time, "%Y-%m-%d %H:%M:%S.%f")
        remaining_time = PACK_COOLDOWN - (datetime.now() - last_open_time)

        if remaining_time > timedelta(0):  # Если время ещё не вышло
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes = remainder // 60
            await message.answer(f"⌛ Вы недавно открывали пак. Подождите ещё {hours} ч {minutes} мин!")
            return

    card = get_random_card()
    
    if not card:
        await message.answer("Не удалось открыть пак, попробуйте позже.")
        return
    
    # Обновляем время и добавляем карту в инвентарь
    update_last_open_time(user_id)
    add_card_to_collection(user_id, card["card_id"])
    
    card_image = FSInputFile(f"photo/{card['card_id']}.jpg")
    caption = f"🎴 <b>{card['name']}</b>\n⭐ Редкость: {card['rarity'].capitalize()}\n🏆 ID карты: {card['card_id']}\n🔥 Рейтинг: {card['rating']}"
    
    await message.answer_photo(card_image, caption=caption)
