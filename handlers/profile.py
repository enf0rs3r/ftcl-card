from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router
from database.db import get_user_stats  # Импортируем функцию получения статистики
from handlers.collection import collection_handler  # <-- Добавил импорт обработчика коллекции

# Инициализация роутера
router = Router()

# Обработчик кнопки "Статистика"
@router.message(lambda message: message.text == "📝 Статистика")
async def statistics_handler(message: types.Message):
    user_id = message.from_user.id
    stats = get_user_stats(user_id)

    response_text = (
        f"📊 Ваша статистика:\n"
        f"📦 Открыто паков: {stats['packs_opened']}\n"
        f"🏆 Лучшая карточка: Не реализовано в бета-версии\n" # {stats['best_card'][0]} ({stats['best_card'][1]})
        f"⭐ Средний рейтинг: Не реализовано в бета-версии" # {stats['avg_rating']}
    )

    await message.answer(response_text)

# Обработчик кнопки "Коллекция"
@router.message(lambda message: message.text == "🎴 Коллекция")
async def collection_button_handler(message: types.Message):
    await collection_handler(message)  # Теперь вызываем из другого модуля

# Обработчик кнопки "Назад"
@router.message(lambda message: message.text == "🔙 Назад")
async def back_handler(message: types.Message):
    # Возвращаем пользователя в главное меню
    await message.answer("Выберите действие:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏢 Магазин"), KeyboardButton(text="📅 Профиль")]],
        resize_keyboard=True
    ))
