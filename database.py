"""
Модуль для работы с базой данных SQLite
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from config import DATABASE_PATH


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        """Создать таблицы для хранения истории разговоров"""
        cursor = self.conn.cursor()

        # Таблица для хранения сообщений
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                agent_type TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица для хранения активного агента пользователя
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_agents (
                user_id INTEGER PRIMARY KEY,
                current_agent TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def add_message(self, user_id: int, agent_type: str, role: str, content: str):
        """Добавить сообщение в историю"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO messages (user_id, agent_type, role, content) VALUES (?, ?, ?, ?)",
            (user_id, agent_type, role, content)
        )
        self.conn.commit()

    def get_history(self, user_id: int, agent_type: str, limit: int = 20) -> List[Dict]:
        """Получить историю разговора с агентом"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT role, content, timestamp
            FROM messages
            WHERE user_id = ? AND agent_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (user_id, agent_type, limit)
        )

        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2]
            })

        # Возвращаем в хронологическом порядке
        return list(reversed(messages))

    def clear_history(self, user_id: int, agent_type: str):
        """Очистить историю разговора с агентом"""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM messages WHERE user_id = ? AND agent_type = ?",
            (user_id, agent_type)
        )
        self.conn.commit()

    def set_current_agent(self, user_id: int, agent_type: str):
        """Установить текущего агента для пользователя"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO user_agents (user_id, current_agent, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (user_id, agent_type)
        )
        self.conn.commit()

    def get_current_agent(self, user_id: int) -> Optional[str]:
        """Получить текущего агента пользователя"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT current_agent FROM user_agents WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def close(self):
        """Закрыть соединение с базой данных"""
        self.conn.close()
