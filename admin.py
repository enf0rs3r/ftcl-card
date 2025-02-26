from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from database.db import add_card_to_collection, get_card_by_id
from bot_instance import bot

router = Router()

# Список ID администраторов
ADMINS = [5259325234, 7498124027]  # Замени на реальные ID админов

@router.message(Command("give_card"))
async def give_card(message: types.Message):
    """Выдача карточки пользователю по команде /give_card user_id card_id"""
    if message.from_user.id not in ADMINS:
        await message.reply("❌ У вас нет прав для выдачи карт!")
        return

    args = message.text.split()
    if len(args) != 3:
        await message.reply("⚠ Используйте формат: /give_card user_id card_id")
        return

    user_id = args[1]
    card_id = args[2]

    # Проверяем, существует ли карта
    card = get_card_by_id(card_id)
    if not card:
        await message.reply("❌ Карточка с таким ID не найдена!")
        return

    # Выдаём карту пользователю
    add_card_to_collection(int(user_id), card_id)

    try:
        # Отправляем пользователю уведомление
        await bot.send_message(
            int(user_id),
            f"🎉 Вам была выдана новая карточка!\n\n"
            f"🎴 <b>{card['name']}</b>\n"
            f"⭐ Редкость: {card['rarity'].capitalize()}\n"
            f"🏆 ID карты: {card['card_id']}\n"
            f"🔥 Рейтинг: {card['rating']}"
        )
        await message.reply(f"✅ Карточка {card['name']} (ID: {card_id}) успешно выдана пользователю {user_id}!")
    except TelegramBadRequest:
        await message.reply("⚠ Не удалось отправить сообщение пользователю. Возможно, он не подписан на бота.")
