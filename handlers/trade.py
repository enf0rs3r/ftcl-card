from aiogram import Router, types
from database.db import create_trade, confirm_trade, cancel_trade, get_user_card

router = Router()

# Начало трейда
@router.message(lambda message: message.text and message.text.startswith("/trade"))
async def start_trade(message: types.Message):
    args = message.text.split()
    if len(args) != 4:
        await message.answer("Использование: /trade @username card1_id card2_id")
        return
    
    user2 = args[1].replace("@", "")  # Убираем @
    card1_id = int(args[2])
    card2_id = int(args[3])

    # Проверяем, есть ли у игрока 1 нужная карта
    user1_id = message.from_user.id
    if not get_user_card(user1_id, card1_id):
        await message.answer("У вас нет этой карты!")
        return

    # Проверяем, есть ли у второго игрока указанная карта
    if not get_user_card(user2, card2_id):
        await message.answer(f"Игрок @{user2} не имеет карту {card2_id}!")
        return

    # Создаём трейд-запрос в БД
    trade_id = create_trade(user1_id, user2, card1_id, card2_id)

    await message.answer(
        f"@{user2}, вам предложен обмен!\n"
        f"Вы получите карту {card1_id}, отдав {card2_id}.\n"
        f"Подтвердите обмен командой: /confirm_trade {trade_id}"
    )

# Подтверждение трейда
@router.message(lambda message: message.text and message.text.startswith("/confirm_trade"))
async def confirm_trade_handler(message: types.Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Использование: /confirm_trade trade_id")
        return

    trade_id = int(args[1])
    
    if confirm_trade(trade_id):
        await message.answer("Обмен успешно завершён! Карты поменялись.")
    else:
        await message.answer("Ошибка! Обмен не найден или уже завершён.")

# Отмена трейда
@router.message(lambda message: message.text and message.text.startswith("/cancel_trade"))
async def cancel_trade_handler(message: types.Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Использование: /cancel_trade trade_id")
        return

    trade_id = int(args[1])
    cancel_trade(trade_id)
    await message.answer("Обмен отменён.")
