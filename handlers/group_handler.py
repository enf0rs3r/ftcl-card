from aiogram import Router
from aiogram.types import Message, FSInputFile, ChatMemberUpdated
from database.db import add_card_to_collection, get_last_open_time, update_last_open_time
import json
import random
from datetime import datetime, timedelta

router = Router()

RARITY_CHANCES = {
    "common": 70,
    "rare": 17,
    "epic": 10,
    "legendary": 3
}

PACK_COOLDOWN = timedelta(hours=7)  # 10 часов задержка

@router.chat_member()
async def welcome_bot(event: ChatMemberUpdated):
    """Приветствие при добавлении бота в группу"""
    if event.new_chat_member.user.id == event.bot.id:
        await event.chat.send_message(
            f"👋 Привет! Я бот карточек ФТКЛ. Сделайте меня администратором (очень важный пункт, я не буду работать без этого!) и напишите 'фтклкарта', чтобы открыть пак! ⚽"
        )

def load_cards():
    with open("data/cards.json", "r", encoding="utf-8") as file:
        return json.load(file)

def get_random_card():
    cards = load_cards()
    rarity = random.choices(list(RARITY_CHANCES.keys()), weights=RARITY_CHANCES.values(), k=1)[0]
    filtered_cards = [card for card in cards if card["rarity"] == rarity]
    return random.choice(filtered_cards) if filtered_cards else None

@router.message(lambda msg: msg.chat.type in ["group", "supergroup"] and msg.text and msg.text.lower() in ["фтклкарта", "ебалай, дай мне карту", "ну и где моя карта?"])
async def group_pack_handler(message: Message):
    user_id = message.from_user.id
    last_open_time = get_last_open_time(user_id)

    if last_open_time:
        last_open_time = datetime.strptime(last_open_time, "%Y-%m-%d %H:%M:%S.%f")
        remaining_time = PACK_COOLDOWN - (datetime.now() - last_open_time)
        if remaining_time.total_seconds() > 0:
            hours, minutes = divmod(remaining_time.total_seconds() // 60, 60)
            await message.reply(f"⌛ Подождите {int(hours)}ч {int(minutes)}м до следующего пака!")
            await message.reply(f"Хочешь открыть ещё? В ЛС бота есть бесконечный пак - проверь сам!")
            return

    card = get_random_card()
    if not card:
        await message.reply("Не удалось открыть пак, попробуйте позже.")
        return

    update_last_open_time(user_id)
    add_card_to_collection(user_id, card["card_id"])

    card_image = FSInputFile(f"photo/{card['card_id']}.jpg")
    caption = f"🎴 <b>{card['name']}</b>\n⭐ Редкость: {card['rarity'].capitalize()}\n🏆 ID карты: {card['card_id']}\n🔥 Рейтинг: {card['rating']}\nКарта была добавлена в вашу коллекцию (в ЛС бота)"

    await message.reply_photo(card_image, caption=caption)
