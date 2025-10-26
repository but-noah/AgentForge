"""Redis caching service."""

import os
import json
from typing import Any, Optional
import redis.asyncio as redis


class RedisCache:
    """Service for caching data in Redis."""

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Establish connection to Redis."""
        try:
            self.client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.client.ping()
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if not self.client:
                await self.connect()

            value = await self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"Error getting from cache: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional expiration (in seconds)."""
        try:
            if not self.client:
                await self.connect()

            # Serialize value
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value)
            else:
                serialized = str(value)

            if expire:
                await self.client.setex(key, expire, serialized)
            else:
                await self.client.set(key, serialized)

            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if not self.client:
                await self.connect()

            await self.client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting from cache: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if not self.client:
                await self.connect()

            return await self.client.exists(key) > 0
        except Exception as e:
            print(f"Error checking cache existence: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in cache."""
        try:
            if not self.client:
                await self.connect()

            return await self.client.incrby(key, amount)
        except Exception as e:
            print(f"Error incrementing cache: {e}")
            raise

    async def set_hash(self, key: str, mapping: dict) -> bool:
        """Set multiple fields in a hash."""
        try:
            if not self.client:
                await self.connect()

            # Serialize dict values
            serialized_mapping = {
                k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                for k, v in mapping.items()
            }

            await self.client.hset(key, mapping=serialized_mapping)
            return True
        except Exception as e:
            print(f"Error setting hash: {e}")
            return False

    async def get_hash(self, key: str) -> Optional[dict]:
        """Get all fields from a hash."""
        try:
            if not self.client:
                await self.connect()

            data = await self.client.hgetall(key)
            if not data:
                return None

            # Deserialize values
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except json.JSONDecodeError:
                    result[k] = v

            return result
        except Exception as e:
            print(f"Error getting hash: {e}")
            return None

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        try:
            if not self.client:
                await self.connect()

            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Error clearing pattern: {e}")
            return 0
