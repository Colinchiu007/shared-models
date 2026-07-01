"""
缓存模块 — 从 MediaCrawler cache 适配

提供统一的缓存抽象层，支持内存缓存和 Redis 缓存。

使用:
    from shared_models.cache import CacheFactory, MemoryCache

    # 快速使用
    cache = CacheFactory.create_cache("memory")
    cache.set("key", {"data": 123}, 60)
    value = cache.get("key")

    # 全局默认缓存（单例）
    from shared_models.cache import get_cache
    cache = get_cache()
"""

from .abs_cache import AbstractCache
from .cache_factory import CacheFactory
from .memory_cache import MemoryCache

try:
    from .redis_cache import RedisCache
except ImportError:
    RedisCache = None  # type: ignore[assignment, misc]

__all__ = [
    "AbstractCache",
    "CacheFactory",
    "MemoryCache",
]

if RedisCache is not None:
    __all__.append("RedisCache")


def get_cache() -> AbstractCache:
    """获取全局默认缓存（等价于 CacheFactory.get_default()）"""
    return CacheFactory.get_default()
