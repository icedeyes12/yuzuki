import asyncpg
import os
from datetime import datetime
from typing import List, Dict, Optional
import json
from copy import deepcopy

# Database config - ALL from env vars, no defaults for secrets
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "yuzuki")
DB_USER = os.getenv("DB_USER", "yuzuki")
DB_PASS = os.getenv("DB_PASS")  # Required - set in .env file

if not DB_PASS:
    raise ValueError("DB_PASS environment variable is required!")


class YuzukiDatabase:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                min_size=2,
                max_size=10,
            )

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT NOT NULL,
                    is_owner BOOLEAN DEFAULT FALSE,
                    is_blocked BOOLEAN DEFAULT FALSE,
                    blocked_at TIMESTAMP,
                    blocked_by BIGINT,
                    block_reason TEXT,
                    memory_json JSONB DEFAULT '{}',
                    message_count INTEGER DEFAULT 0,
                    last_seen TIMESTAMP DEFAULT NOW()
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS blocked_users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    blocked_by BIGINT NOT NULL,
                    reason TEXT,
                    blocked_at TIMESTAMP DEFAULT NOW(),
                    unblocked_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id BIGINT PRIMARY KEY,
                    channel_id BIGINT,
                    guild_id BIGINT,
                    thread_id BIGINT,
                    user_id BIGINT NOT NULL,
                    username TEXT NOT NULL,
                    content TEXT,
                    is_bot_response BOOLEAN DEFAULT FALSE,
                    is_dm BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT UNIQUE NOT NULL,
                    user_id BIGINT NOT NULL,
                    channel_id BIGINT,
                    guild_id BIGINT,
                    dm_access_level TEXT DEFAULT 'normal',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)

    async def store_message(
        self,
        message_id: int,
        channel_id: int,
        guild_id: Optional[int],
        user_id: int,
        username: str,
        content: str,
        is_bot_response: bool = False,
        is_dm: bool = False,
        thread_id: Optional[int] = None,
    ):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO messages (message_id, channel_id, guild_id, thread_id,
                                    user_id, username, content, is_bot_response, is_dm)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (message_id) DO NOTHING
                """,
                message_id, channel_id, guild_id, thread_id,
                user_id, username, content, is_bot_response, is_dm,
            )

            await conn.execute(
                """
                INSERT INTO users (user_id, username, last_seen)
                VALUES ($1, $2, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET username = $2, last_seen = NOW()
                """,
                user_id, username,
            )

    async def get_memory(self, user_id: int) -> Dict:
        """Get user's memory profile."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT memory_json FROM users WHERE user_id = $1", user_id
            )
            return row["memory_json"] if row and row["memory_json"] else {}

    async def merge_memory(self, user_id: int, new_data: Dict) -> Dict:
        """Deep merge new_data into user's memory_json. Returns merged result."""
        async with self.pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT memory_json FROM users WHERE user_id = $1", user_id
            )
            current = existing["memory_json"] if existing and existing["memory_json"] else {}

            merged = deepcopy(current)
            for key, value in new_data.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = {**merged[key], **value}
                elif key == "metadata":
                    if "metadata" not in merged:
                        merged["metadata"] = {}
                    merged["metadata"]["last_updated"] = datetime.now().isoformat()
                    if "sessions_analyzed" in value:
                        merged["metadata"]["sessions_analyzed"] = (
                            merged["metadata"].get("sessions_analyzed", 0) + value["sessions_analyzed"]
                        )
                    if "total_messages" in value:
                        merged["metadata"]["total_messages"] = (
                            merged["metadata"].get("total_messages", 0) + value["total_messages"]
                        )
                else:
                    merged[key] = value

            await conn.execute(
                "UPDATE users SET memory_json = $2 WHERE user_id = $1",
                user_id, json.dumps(merged),
            )
            return merged

    async def increment_message_count(self, user_id: int) -> int:
        """Increment user's message count. Returns new count."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO users (user_id, message_count)
                VALUES ($1, 1)
                ON CONFLICT (user_id)
                DO UPDATE SET message_count = users.message_count + 1
                RETURNING message_count
                """,
                user_id,
            )
            return row["message_count"]

    async def reset_message_count(self, user_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET message_count = 0 WHERE user_id = $1", user_id
            )

    async def get_recent_messages(
        self,
        user_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        limit: int = 30,
    ) -> List[Dict]:
        async with self.pool.acquire() as conn:
            if user_id:
                rows = await conn.fetch(
                    """
                    SELECT user_id, username, content, is_bot_response, created_at
                    FROM messages
                    WHERE user_id = $1 AND is_dm = TRUE
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    user_id, limit,
                )
            elif channel_id:
                rows = await conn.fetch(
                    """
                    SELECT user_id, username, content, is_bot_response, created_at
                    FROM messages
                    WHERE channel_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    channel_id, limit,
                )
            else:
                return []

            return [
                {
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "content": row["content"],
                    "is_bot": row["is_bot_response"],
                    "created_at": row["created_at"],
                }
                for row in reversed(rows)
            ]

    async def is_user_blocked(self, user_id: int) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT is_blocked FROM users WHERE user_id = $1", user_id
            )
            if row and row["is_blocked"]:
                return True

            row2 = await conn.fetchrow(
                "SELECT 1 FROM blocked_users WHERE user_id = $1 AND is_active = TRUE",
                user_id,
            )
            return row2 is not None

    async def block_user(self, user_id: int, blocked_by: int, reason: str = ""):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (user_id, is_blocked, blocked_at, blocked_by, block_reason)
                VALUES ($1, TRUE, NOW(), $2, $3)
                ON CONFLICT (user_id)
                DO UPDATE SET is_blocked = TRUE, blocked_at = NOW(),
                              blocked_by = $2, block_reason = $3
                """,
                user_id, blocked_by, reason,
            )

            await conn.execute(
                "INSERT INTO blocked_users (user_id, blocked_by, reason) VALUES ($1, $2, $3)",
                user_id, blocked_by, reason,
            )

    async def unblock_user(self, user_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_blocked = FALSE, block_reason = NULL WHERE user_id = $1",
                user_id,
            )
            await conn.execute(
                "UPDATE blocked_users SET is_active = FALSE, unblocked_at = NOW() "
                "WHERE user_id = $1 AND is_active = TRUE",
                user_id,
            )

    async def get_all_recent_messages(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get all recent messages for a user (both DM and non-DM) for summarization."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT user_id, username, content, is_bot_response, created_at, is_dm
                FROM messages
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                user_id, limit,
            )
            return [
                {
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "content": row["content"],
                    "is_bot": row["is_bot_response"],
                    "created_at": row["created_at"],
                    "is_dm": row["is_dm"],
                }
                for row in reversed(rows)
            ]


db = YuzukiDatabase()
