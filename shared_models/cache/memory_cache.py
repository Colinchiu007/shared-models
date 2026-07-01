"""
内存缓存实现 — 从 MediaCrawler cache/local_cache.py 适配

使用 dict 存储，惰性过期检查（get 时检查）。无后台清理任务，
避免 asyncio task 泄漏。

特点：
- 线程安全（普通场景）
- 惰性过期：仅在访问时检查 TTL
- 无异步依赖：不需要 event loop
"""

import time
from typing import Any, Dict, List, Optional, Tuple

from .abs_cache import AbstractCache


class MemoryCache(AbstractCache):
    """基于内存的缓存实现（惰性过期）"""

    def __init__(self):
        self._data: Dict[str, Tuple[Any, float]] = {}
        # _data[key] = (value, expire_at_timestamp)

    def get(self, key: str) -> Optional[Any]:
        value, expire_at = self._data.get(key, (None, 0))
        if value is None:
            return None
        if expire_at < time.time():
            del self._data[key]
            return None
        return value

    def set(self, key: str, value: Any, expire_time: int) -> None:
        self._data[key] = (value, time.time() + expire_time)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def keys(self, pattern: str) -> List[str]:
        if pattern == '*':
            return list(self._data.keys())
        pat = pattern.replace('*', '')
        return [k for k in self._data if pat in k]

    def clear(self) -> None:
        self._data.clear()

    @property
    def size(self) -> int:
        """当前缓存条目数"""
        return len(self._data)
