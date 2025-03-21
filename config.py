import os

# Токен бота, полученный через BotFather
TOKEN = "7936215498:AAE432BQFdYDBNRxuEeWlbZNzEX8zUeJupk"  # Заменить на свой токен

# Путь к базе данных (для SQLite)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "cards.db")

# В случае, если бы ты использовал PostgreSQL:
# DATABASE_URL = "postgresql://user:password@localhost/dbname"
