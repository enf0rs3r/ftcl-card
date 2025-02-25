import logging
import asyncio
import os
import requests
from flask import Flask
from threading import Thread
from bot_instance import bot, dp
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

# Flask-заглушка
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run_server():
    """Запуск Flask в отдельном потоке"""
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False)

# Запускаем Flask в фоне
Thread(target=run_server, daemon=True).start()

async def ping_self():
    """Периодически делает запросы к самому себе, чтобы Render не завершал процесс"""
    while True:
        try:
            url = os.getenv("RENDER_EXTERNAL_URL")  # Render даёт переменную с внешним URL
            if url:
                requests.get(url)
                logging.info("Pinged self to keep alive")
        except Exception as e:
            logging.error(f"Ping failed: {e}")
        await asyncio.sleep(600)  # Каждые 10 минут

async def main():
    """Запуск бота и пингов"""
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(ping_self())  # Запускаем пинг в фоне
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
