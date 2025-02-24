import json
import random
from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from database.db import add_card_to_collection

router = Router()

def load_cards():
    """Загружает карточки из cards.json"""
    with open("data/cards.json", "r", encoding="utf-8") as file:
        return json.load(file)

def get_common_card():
    """Выбирает случайную карту только с обычной (common) редкостью"""
    cards = load_cards()
    common_cards = [card for card in cards if card["rarity"] == "common"]
    
    if not common_cards:
        return None  # Если вдруг нет карт с этой редкостью
    
    return random.choice(common_cards)

@router.message(Command("endless_pack"))
async def endless_pack(message: Message):
    """Обработчик команды /endless_pack"""
    user_id = message.from_user.id
    card = get_common_card()
    
    if not card:
        await message.answer("Не удалось открыть бесконечный пак, попробуйте позже.")
        return
    
    # Добавляем карту в инвентарь
    add_card_to_collection(user_id, card["card_id"])
    
    card_image = FSInputFile(f"photo/{card['card_id']}.jpg")
    caption = f"🎴 <b>{card['name']}</b>\n⭐ Редкость: {card['rarity'].capitalize()}\n🏆 ID карты: {card['card_id']}\n🔥 Рейтинг: {card['rating']}"
    
    await message.answer_photo(card_image, caption=caption)
