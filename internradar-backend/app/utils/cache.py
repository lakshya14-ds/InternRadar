"""Resilient cache utility with Redis and in-memory fallback."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CacheManager:
    """Resilient caching layer that uses Redis but falls back to in-memory dictionary if Redis is unavailable."""

    def __init__(self) -> None:
        self.redis_client = None
        self.memory_db: dict[str, Any] = {}

        try:
            import redis  # type: ignore
            from app.config import get_settings

            settings = get_settings()
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_db,
                socket_timeout=2.0,
                decode_responses=True,
            )
            # Ping to verify connection
            self.redis_client.ping()
            logger.info("Connected to Redis cache successfully")
        except Exception as exc:
            logger.warning("Redis is unavailable (falling back to in-memory cache): %s", exc)
            self.redis_client = None

    def get(self, key: str) -> Any | None:
        if self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as exc:
                logger.warning("Redis GET failed (using memory cache): %s", exc)
        return self.memory_db.get(key)

    def set(self, key: str, value: Any, expire_seconds: int | None = None) -> None:
        if self.redis_client:
            try:
                self.redis_client.set(key, value, ex=expire_seconds)
                return
            except Exception as exc:
                logger.warning("Redis SET failed (using memory cache): %s", exc)
        self.memory_db[key] = value

    def exists(self, key: str) -> bool:
        if self.redis_client:
            try:
                return bool(self.redis_client.exists(key))
            except Exception as exc:
                logger.warning("Redis EXISTS failed (using memory cache): %s", exc)
        return key in self.memory_db


# Global singleton instance
cache = CacheManager()
