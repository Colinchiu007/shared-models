"""
缓存工厂 — 从 MediaCrawler cache/cache_factory.py 适配

根据配置创建对应的缓存后端实例。

使用:
    cache = CacheFactory.create_cache("memory")
    cache.set("key", "value", 60)
    val = cache.get("key")

    cache = CacheFactory.create_cache("redis", host="localhost", port=6379)
"""

from typing import Any, Optional

from .abs_cache import AbstractCache


class CacheFactory:
    """缓存工厂"""

    _default_instance: Optional[AbstractCache] = None

    @staticmethod
    def create_cache(cache_type: str = "memory", **kwargs) -> AbstractCache:
        """
        创建缓存实例

        Args:
            cache_type: 缓存类型 ("memory" / "redis")
            **kwargs: 传递给缓存实现的参数

        Returns:
            AbstractCache 实例
        """
        if cache_type == "memory":
            from .memory_cache import MemoryCache
            return MemoryCache(**kwargs)

        if cache_type == "redis":
            from .redis_cache import RedisCache
            return RedisCache(**kwargs)

        supported = ", ".join(["memory", "redis"])
        raise ValueError(f"不支持的缓存类型: {cache_type!r}。支持: {supported}")

    @classmethod
    def get_default(cls) -> AbstractCache:
        """获取全局默认缓存实例（单例）"""
        if cls._default_instance is None:
            cls._default_instance = cls.create_cache("memory")
        return cls._default_instance

    @classmethod
    def set_default(cls, cache: AbstractCache) -> None:
        """设置全局默认缓存实例"""
        cls._default_instance = cache
