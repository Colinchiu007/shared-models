"""
缓存抽象基类 — 从 MediaCrawler cache/abs_cache.py 适配

提供统一的缓存接口，供 MemoryCache / RedisCache 实现。
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class AbstractCache(ABC):
    """缓存抽象基类"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        :param key: 键
        :return: 值（不存在返回 None）
        """
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: Any, expire_time: int) -> None:
        """
        设置缓存值
        :param key: 键
        :param value: 值
        :param expire_time: 过期时间（秒）
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        """删除缓存值"""
        raise NotImplementedError

    @abstractmethod
    def keys(self, pattern: str) -> List[str]:
        """
        获取匹配模式的键列表
        :param pattern: 匹配模式（如 '*' 匹配所有）
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """清空缓存"""
        raise NotImplementedError
