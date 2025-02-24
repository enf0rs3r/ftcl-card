import sqlite3
import json

DB_PATH = "database/cards.db"  # Укажи свой путь к БД
JSON_PATH = "data/cards.json"  # Укажи путь к JSON-файлу

def get_rarity(rating):
    """Функция для определения редкости по рейтингу"""
    if rating >= 90:
        return "легендарная"
    elif rating >= 80:
        return "эпическая"
    elif rating >= 70:
        return "редкая"
    else:
        return "обычная"

def update_cards():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Загружаем JSON
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        cards_data = json.load(f)

    # Добавляем или обновляем карты в БД
    for card in cards_data:
        rarity = get_rarity(card["rating"])  # Определяем редкость
        cursor.execute('''
            INSERT INTO cards (card_id, name, rating, rarity)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(card_id) DO UPDATE SET 
                name = excluded.name,
                rating = excluded.rating,
                rarity = excluded.rarity
        ''', (card["card_id"], card["name"], card["rating"], rarity))

    conn.commit()
    conn.close()
    print("✅ Таблица карт обновлена!")

if __name__ == "__main__":
    update_cards()
