from aiogram import Router, types
import asyncio
from database.db import get_user_collection

router = Router()

async def get_user_collection_async(user_id):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_user_collection, user_id)

@router.message(lambda message: message.text == "🎴 Коллекция")
async def collection_handler(message: types.Message):
    user_id = message.from_user.id
    collection = await get_user_collection_async(user_id)
    response_text = "📜 Ваша коллекция:\n\n"

    if not collection or not any(collection.values()):
        response_text = "❌ Ваша коллекция пуста."
        await message.answer(response_text, parse_mode="Markdown")
        return

    for rarity, cards in collection.items():
        if cards:
            if rarity == "легендарная":
                rarity_display = rarity[:-2] + "ые"
            elif rarity == "эпическая":
                rarity_display = rarity[:-2] + "ие"
            elif rarity == "редкая":
                rarity_display = rarity[:-2] + "ие"
            elif rarity == "обычная":
                rarity_display = rarity[:-2] + "ые"
            else:
                rarity_display = rarity

            response_text += f"🔥 *{rarity_display.capitalize()} карты:*\n" + "\n".join(cards) + "\n\n"

    await message.answer(response_text, parse_mode="Markdown")
