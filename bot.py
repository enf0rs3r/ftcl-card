import logging
import asyncio
import os
from time import sleep
from threading import Thread
from flask import Flask
from bot_instance import bot, dp  # Импортируем уже созданные bot и dp
from handlers import start, shop, profile, open_pack, trade, group_handler, endless_pack
from database.db import create_tables

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

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run_server():
    while True:
        try:
            app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
        except Exception as e:
            print(f"Flask error: {e}")
        sleep(5)  # Пауза, чтобы Flask не падал мгновенно

Thread(target=run_server, daemon=True).start()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
