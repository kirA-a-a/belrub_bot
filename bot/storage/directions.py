import sqlite3
from pathlib import Path

from bot.storage import Direction


class DirectionStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_directions (
                    user_id INTEGER PRIMARY KEY,
                    direction TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def get(self, user_id: int) -> Direction | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT direction FROM user_directions WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return Direction(row["direction"])

    def set(self, user_id: int, direction: Direction) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO user_directions (user_id, direction, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    direction = excluded.direction,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, direction.value),
            )
            conn.commit()
