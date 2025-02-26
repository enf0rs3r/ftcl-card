from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable, Dict, Any, Awaitable

CHANNEL_USERNAME = "@ftclcards"  # Укажи юзернейм канала

async def is_subscribed(bot, user_id: int) -> bool:
    """ Проверяет, подписан ли пользователь на канал """
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False

class SubscriptionMiddleware(BaseMiddleware):
    """ Middleware для проверки подписки перед любой командой """
    
    async def __call__(
        self, handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = data.get("event_from_user").id
        bot = data["bot"]

        if not await is_subscribed(bot, user_id):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscription")]
            ])
            await data["event_chat"].send_message("❌ Чтобы пользоваться ботом, подпишитесь на канал!", reply_markup=keyboard)
            return  # Прерываем выполнение команды

        return await handler(event, data)
