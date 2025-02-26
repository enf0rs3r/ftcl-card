from aiogram.types import Update, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from typing import Callable, Dict, Any, Awaitable

CHANNEL_USERNAME = "@ftclcards"  # Замени на юзернейм своего канала

async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """ Проверяет, подписан ли пользователь на канал """
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False

class SubscriptionMiddleware(BaseMiddleware):
    """ Middleware для проверки подписки перед любыми командами """
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        bot: Bot = data["bot"]
        user_id = data["event_from_user"].id

        if not await is_subscribed(bot, user_id):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔔 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]
            ])
            await bot.send_message(user_id, "❌ Чтобы пользоваться ботом, подпишитесь на канал!", reply_markup=keyboard)
            return  # Блокируем выполнение команды

        return await handler(event, data)  # Если подписан, продолжаем обработку
