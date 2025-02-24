import logging
import asyncio
from bot_instance import bot, dp  # Импортируем уже созданные bot и dp
from handlers import start, shop, profile
from handlers import open_pack
from database.db import create_tables
from handlers import trade
from handlers import group_handler
from handlers import endless_pack


create_tables()

# Логирование
logging.basicConfig(level=logging.INFO)

# Подключаем обработчики
dp.include_router(start.router)
dp.include_router(shop.router)
dp.include_router(profile.router)
dp.include_router(open_pack.router)
dp.include_router(trade.router)
dp.include_router(group_handler.router)
dp.include_router(endless_pack.router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

    
