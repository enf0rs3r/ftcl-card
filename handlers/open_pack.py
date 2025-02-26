import json
import random
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, CallbackQuery
from database.db import add_card_to_collection, get_last_open_time, update_last_open_time
from datetime import datetime, timedelta

router = Router()

# Загружаем данные о паках
def load_packs():
    with open("data/packs.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Загружаем данные о картах
def load_cards():
    with open("data/cards.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Выбираем случайную карту в зависимости от шансов редкости
def get_random_card(chances):
    cards = load_cards()
    
    # Выбираем редкость по шансам
    rarity = random.choices(
        list(chances.keys()),
        weights=chances.values(),
        k=1
    )[0]
    
    filtered_cards = [card for card in cards if card["rarity"] == rarity]
    return random.choice(filtered_cards) if filtered_cards else None

# Обработчик для показа информации об обычном паке
@router.message(lambda message: message.text == "📦 Обычный пак")
async def open_pack_info(message: types.Message):
    packs = load_packs()
    normal_pack = next((p for p in packs if p["pack_id"] == "standard"), None)

    if not normal_pack:
        await message.answer("Ошибка: информация о паке не найдена.")
        return

    photo = FSInputFile(f"photo/{normal_pack['photo']}")
    text = (f"📦 <b>{normal_pack['name']}</b>\n"
            f"💰 Цена: {normal_pack['price']} монет\n"
            f"⏳ Интервал: {normal_pack['interval']} ч\n"
            f"🎲 Шансы:\n"
            + "\n".join([f"  - {rarity.capitalize()}: {chance}%" for rarity, chance in normal_pack["chances"].items()]))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Открыть", callback_data="open_normal_pack")]
    ])

    await message.answer_photo(photo, caption=text, reply_markup=keyboard)

# Обработчик нажатия кнопки "Открыть" для обычного пака
@router.callback_query(lambda c: c.data == "open_normal_pack")
async def open_normal_pack(call: CallbackQuery):
    user_id = call.from_user.id
    packs = load_packs()
    normal_pack = next((p for p in packs if p["pack_id"] == "standard"), None)

    if not normal_pack:
        await call.message.answer("Ошибка: информация о паке не найдена.")
        return

    last_open_time = get_last_open_time(user_id)
    cooldown = timedelta(hours=normal_pack["interval"])

    if last_open_time:
        last_open_time = datetime.strptime(last_open_time, "%Y-%m-%d %H:%M:%S.%f")
        remaining_time = cooldown - (datetime.now() - last_open_time)

        if remaining_time > timedelta(0):  # Если время ещё не вышло
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes = remainder // 60
            await call.message.answer(f"⌛ Вы недавно открывали пак. Подождите ещё {hours} ч {minutes} мин!")
            return

    card = get_random_card(normal_pack["chances"])

    if not card:
        await call.message.answer("Не удалось открыть пак, попробуйте позже.")
        return

    update_last_open_time(user_id)
    add_card_to_collection(user_id, card["card_id"])

    card_image = FSInputFile(f"photo/{card['card_id']}.jpg")
    caption = (f"🎴 <b>{card['name']}</b>\n"
               f"⭐ Редкость: {card['rarity'].capitalize()}\n"
               f"🏆 ID карты: {card['card_id']}\n"
               f"🔥 Рейтинг: {card['rating']}")

    await call.message.answer_photo(card_image, caption=caption)
