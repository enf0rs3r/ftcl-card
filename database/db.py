import sqlite3
from datetime import datetime

# Путь к базе данных
DB_PATH = "database/cards.db"

# Создание таблиц
def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 1000,
            last_open_time DATETIME,
            opened_packs INTEGER DEFAULT 0
        )
    ''')

    # Таблица карточек
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS cards (
            card_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            rarity TEXT,
            price INTEGER,
            rating INTEGER DEFAULT 0
        )
    ''')

    # Таблица инвентаря пользователя
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS user_cards (
            user_id INTEGER,
            card_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (card_id) REFERENCES cards (card_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection (
            user_id INTEGER,
            card_id INTEGER,
            quantity INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, card_id)
        )
    ''')

    conn.commit()
    conn.close()

# Добавление нового пользователя
def add_user(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

# Обновление количества открытых паков
def update_opened_packs(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET opened_packs = opened_packs + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Получение количества открытых паков
def get_opened_packs(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT opened_packs FROM users WHERE user_id = ?", (user_id,))
    packs = cursor.fetchone()
    conn.close()
    return packs[0] if packs else 0

# Получение лучшей карточки пользователя
def get_best_card(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT cards.name, cards.rating 
        FROM user_cards 
        JOIN cards ON user_cards.card_id = cards.card_id
        WHERE user_cards.user_id = ?
        ORDER BY cards.rating DESC
        LIMIT 1
    ''', (user_id,))
    best_card = cursor.fetchone()
    conn.close()
    return best_card if best_card else ("Нет карт", 0)

# Получение среднего рейтинга карт пользователя
def get_average_rating(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT AVG(cards.rating) 
        FROM user_cards 
        JOIN cards ON user_cards.card_id = cards.card_id
        WHERE user_cards.user_id = ?
    ''', (user_id,))
    avg_rating = cursor.fetchone()
    conn.close()
    return round(avg_rating[0], 2) if avg_rating[0] else 0

# Получение общего среднего рейтинга всех игроков
def get_overall_average_rating():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT AVG(cards.rating) 
        FROM user_cards 
        JOIN cards ON user_cards.card_id = cards.card_id
    ''')
    avg_rating = cursor.fetchone()
    conn.close()
    return round(avg_rating[0], 2) if avg_rating[0] else 0

# Добавление карточки в таблицу карточек
def add_card(name, rarity, price, rating):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cards (name, rarity, price, rating) VALUES (?, ?, ?, ?)", (name, rarity, price, rating))
    conn.commit()
    conn.close()

# Получение информации о карточке по id
def get_card_by_id(card_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards WHERE card_id = ?", (card_id,))
    card = cursor.fetchone()
    conn.close()
    return card

# Добавление карточки в инвентарь пользователя
def add_card_to_inventory(user_id, card_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_cards (user_id, card_id) VALUES (?, ?)", (user_id, card_id))
    conn.commit()
    conn.close()

# Получение времени последнего открытия пака
def get_last_open_time(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT last_open_time FROM users WHERE user_id = ?", (user_id,))
    last_open_time = cursor.fetchone()
    conn.close()
    return last_open_time[0] if last_open_time else None

def update_last_open_time(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()  # Убедись, что создаётся курсор
    cursor.execute("UPDATE users SET last_open_time = ? WHERE user_id = ?", (datetime.now(), user_id))
    conn.commit()
    conn.close()

# Получение статистики пользователя
def get_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Количество открытых паков
    cursor.execute("SELECT COUNT(*) FROM user_cards WHERE user_id = ?", (user_id,))
    packs_opened = cursor.fetchone()[0]
    
    # Лучшая карточка по рейтингу
    cursor.execute("""
        SELECT cards.name, cards.rarity, cards.price 
        FROM user_cards
        JOIN cards ON user_cards.card_id = cards.card_id
        WHERE user_cards.user_id = ?
        ORDER BY cards.price DESC LIMIT 1
    """, (user_id,))
    best_card = cursor.fetchone()
    
    # Средний рейтинг карточек пользователя
    cursor.execute("""
        SELECT AVG(cards.price) 
        FROM user_cards
        JOIN cards ON user_cards.card_id = cards.card_id
        WHERE user_cards.user_id = ?
    """, (user_id,))
    avg_rating = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "packs_opened": packs_opened,
        "best_card": best_card if best_card else ("-", "-", 0),
        "avg_rating": round(avg_rating, 2) if avg_rating else 0
    }

def get_best_card(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cards.name, cards.rarity, cards.rating
        FROM user_cards
        JOIN cards ON user_cards.card_id = cards.card_id
        WHERE user_cards.user_id = ?
        ORDER BY cards.rating DESC
        LIMIT 1
    ''', (user_id,))
    best_card = cursor.fetchone()
    conn.close()

    print(f"Лучшая карточка пользователя {user_id}: {best_card}")  # Отладочный вывод

    return best_card

# Таблица обменов
def create_trade_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER,
            user2_id INTEGER,
            card1_id INTEGER,
            card2_id INTEGER,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user1_id) REFERENCES users (user_id),
            FOREIGN KEY (user2_id) REFERENCES users (user_id),
            FOREIGN KEY (card1_id) REFERENCES cards (card_id),
            FOREIGN KEY (card2_id) REFERENCES cards (card_id)
        )
    ''')
    conn.commit()
    conn.close()

# Вызови эту функцию в bot.py сразу после create_tables()
create_trade_table()

# Создание трейда
def create_trade(user1_id, user2_id, card1_id, card2_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trades (user1_id, user2_id, card1_id, card2_id) VALUES (?, ?, ?, ?)",
        (user1_id, user2_id, card1_id, card2_id)
    )
    conn.commit()
    conn.close()

# Получение трейда по ID
def get_trade(trade_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades WHERE trade_id = ?", (trade_id,))
    trade = cursor.fetchone()
    conn.close()
    return trade

# Подтверждение трейда
def confirm_trade(trade_id):
    trade = get_trade(trade_id)
    if not trade:
        return False

    user1_id, user2_id, card1_id, card2_id = trade[1], trade[2], trade[3], trade[4]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Удаляем старые карты
    cursor.execute("DELETE FROM user_cards WHERE user_id = ? AND card_id = ?", (user1_id, card1_id))
    cursor.execute("DELETE FROM user_cards WHERE user_id = ? AND card_id = ?", (user2_id, card2_id))
    
    # Обмениваем карты
    cursor.execute("INSERT INTO user_cards (user_id, card_id) VALUES (?, ?)", (user1_id, card2_id))
    cursor.execute("INSERT INTO user_cards (user_id, card_id) VALUES (?, ?)", (user2_id, card1_id))
    
    # Обновляем статус трейда
    cursor.execute("UPDATE trades SET status = 'completed' WHERE trade_id = ?", (trade_id,))
    
    conn.commit()
    conn.close()
    return True

# Отмена трейда
def cancel_trade(trade_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE trades SET status = 'canceled' WHERE trade_id = ?", (trade_id,))
    conn.commit()
    conn.close()

# Проверка наличия карты у игрока
def get_trade_by_card(user_id, card_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_cards WHERE user_id = ? AND card_id = ?", (user_id, card_id))
    card = cursor.fetchone()
    conn.close()
    return card

# Экспорт всех карточек пользователей в текстовый файл
def export_user_cards():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT users.user_id, users.username, cards.name, cards.rarity, cards.price 
        FROM user_cards 
        JOIN users ON user_cards.user_id = users.user_id
        JOIN cards ON user_cards.card_id = cards.card_id
        ORDER BY users.user_id
    ''')
    user_cards = cursor.fetchall()
    conn.close()

    with open("user_cards.txt", "w", encoding="utf-8") as file:
        current_user = None
        for user_id, username, name, rarity, price in user_cards:
            if user_id != current_user:
                file.write(f"\n👤 {username} (ID: {user_id})\n")
                file.write("-" * 30 + "\n")
                current_user = user_id
            file.write(f"🎴 {name} | ⭐ {rarity} | 💰 {price} монет\n")
    
    return "user_cards.txt"

def get_user_collection(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cards.card_id, cards.name, cards.rating, cards.rarity, collection.quantity
        FROM collection
        JOIN cards ON collection.card_id = cards.card_id
        WHERE collection.user_id = ?
        ORDER BY 
            CASE 
                WHEN cards.rarity = 'легендарная' THEN 1
                WHEN cards.rarity = 'эпическая' THEN 2
                WHEN cards.rarity = 'редкая' THEN 3
                ELSE 4
            END, cards.rating DESC
    ''', (user_id,))
    
    cards = cursor.fetchall()
    conn.close()

    # Группируем карты по редкости
    collection = {
        "легендарная": [],
        "эпическая": [],
        "редкая": [],
        "обычная": []
    }

    for card_id, name, rating, rarity, quantity in cards:
        collection[rarity].append(f"🎴 {name} (⭐ {rating}) x{quantity}")

    return collection

def get_user_card(user_id, card_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT cards.card_id, cards.name, cards.rating 
        FROM user_cards 
        JOIN cards ON user_cards.card_id = cards.card_id
        WHERE user_cards.user_id = ? AND cards.card_id = ?
    ''', (user_id, card_id))
    card = cursor.fetchone()
    
    conn.close()
    
    return card

def add_card_to_collection(user_id, card_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"Добавляем карту {card_id} пользователю {user_id}")  # Лог

    cursor.execute('''
        INSERT INTO collection (user_id, card_id, quantity)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, card_id) DO UPDATE SET quantity = quantity + 1
    ''', (user_id, card_id))
    conn.commit()
    conn.close()

print(DB_PATH)

def get_common_cards():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT card_id, name FROM cards WHERE rarity = 'обычная'")
    cards = [{"card_id": row[0], "name": row[1]} for row in cursor.fetchall()]

    conn.close()
    return cards

def get_last_endless_open(user_id):
    """Получает время последнего открытия бесконечного пака"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT last_endless_open FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S") if result and result[0] else None

def update_last_endless_open(user_id):
    """Обновляет время последнего открытия бесконечного пака"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE users SET last_endless_open = ? WHERE user_id = ?", (now, user_id))
    
    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO users (user_id, last_endless_open) VALUES (?, ?)", (user_id, now))
    
    conn.commit()
    conn.close()
