"""
Redis 缓存实现 — 从 MediaCrawler cache/redis_cache.py 适配

需要安装 redis 包：
    pip install redis

特点：
- pickle 序列化支持任意 Python 对象
- KEYS 命令优先，不支持时降级为 SCAN（Redis Cluster 兼容）
"""

import pickle
import logging
from typing import Any, List, Optional

from .abs_cache import AbstractCache

logger = logging.getLogger(__name__)

try:
    from redis import Redis
    from redis.exceptions import ResponseError as RedisResponseError
    REDIS_AVAILABLE = True
except ImportError:
    Redis = None  # type: ignore
    RedisResponseError = Exception
    REDIS_AVAILABLE = False


class RedisCache(AbstractCache):
    """基于 Redis 的缓存实现"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0,
                 password: Optional[str] = None, **kwargs):
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis 包未安装。请执行: pip install redis"
            )
        self._client = Redis(
            host=host, port=port, db=db, password=password,
            decode_responses=False, **kwargs
        )

    def get(self, key: str) -> Optional[Any]:
        value = self._client.get(key)
        if value is None:
            return None
        return pickle.loads(value)

    def set(self, key: str, value: Any, expire_time: int) -> None:
        self._client.set(key, pickle.dumps(value), ex=expire_time)

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def keys(self, pattern: str) -> List[str]:
        try:
            raw = self._client.keys(pattern)
            return [k.decode() if isinstance(k, bytes) else k for k in raw]
        except RedisResponseError as e:
            # Redis Cluster 或受限环境不支持 KEYS → 降级 SCAN
            if "unknown command" in str(e).lower():
                keys: List[str] = []
                cursor = 0
                while True:
                    cursor, batch = self._client.scan(
                        cursor=cursor, match=pattern, count=100
                    )
                    keys.extend(
                        k.decode() if isinstance(k, bytes) else k for k in batch
                    )
                    if cursor == 0:
                        break
                return keys
            raise

    def clear(self) -> None:
        # 谨慎使用 — 仅清除当前 db
        self._client.flushdb()
