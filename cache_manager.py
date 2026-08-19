#!/usr/bin/env python3
"""
Cache Manager for Agent Results
Provides caching functionality for agent responses and data queries.
"""

import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from pathlib import Path


class CacheEntry:
    def __init__(self, key: str, value: Any, ttl_seconds: int = 3600):
        self.key = key
        self.value = value
        self.created_at = datetime.utcnow()
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.utcnow() > expiry_time

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'key': self.key,
            'created_at': self.created_at.isoformat(),
            'ttl_seconds': self.ttl_seconds,
            'expired': self.is_expired()
        }


class CacheManager:
    """In-memory cache manager for agent results."""

    def __init__(self, cache_dir: str = ".cache"):
        self.memory_cache = {}
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.stats = {
            'hits': 0,
            'misses': 0,
            'entries': 0
        }

    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate a cache key from data."""
        key_str = f"{prefix}:{json.dumps(data, sort_keys=True, default=str)}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Store value in cache."""
        try:
            entry = CacheEntry(key, value, ttl_seconds)
            self.memory_cache[key] = entry
            self.stats['entries'] = len(self.memory_cache)
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if key not in self.memory_cache:
            self.stats['misses'] += 1
            return None

        entry = self.memory_cache[key]
        if entry.is_expired():
            del self.memory_cache[key]
            self.stats['misses'] += 1
            return None

        self.stats['hits'] += 1
        return entry.value

    def cache_agent_response(self, agent_name: str, input_data: Dict, response: str, ttl_seconds: int = 3600) -> str:
        """Cache an agent response."""
        key = self._generate_key(f"agent:{agent_name}", input_data)
        self.set(key, response, ttl_seconds)
        return key

    def get_cached_response(self, agent_name: str, input_data: Dict) -> Optional[str]:
        """Get cached agent response."""
        key = self._generate_key(f"agent:{agent_name}", input_data)
        return self.get(key)

    def cache_data_query(self, dataset: str, query: Dict, result: Dict, ttl_seconds: int = 1800) -> str:
        """Cache a data query result."""
        key = self._generate_key(f"query:{dataset}", query)
        self.set(key, result, ttl_seconds)
        return key

    def get_cached_query(self, dataset: str, query: Dict) -> Optional[Dict]:
        """Get cached query result."""
        key = self._generate_key(f"query:{dataset}", query)
        return self.get(key)

    def clear(self):
        """Clear all cache."""
        self.memory_cache.clear()
        self.stats['entries'] = 0

    def clear_expired(self) -> int:
        """Clear expired entries and return count."""
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        self.stats['entries'] = len(self.memory_cache)
        return len(expired_keys)

    def get_cache_info(self) -> Dict:
        """Get cache statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            'total_entries': self.stats['entries'],
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'total_requests': total_requests,
            'hit_rate': f"{hit_rate:.1f}%",
            'entries_info': [
                entry.to_dict()
                for entry in self.memory_cache.values()
            ]
        }

    def list_cache_keys(self) -> list[str]:
        """List all cache keys."""
        return list(self.memory_cache.keys())

    def delete(self, key: str) -> bool:
        """Delete specific cache entry."""
        if key in self.memory_cache:
            del self.memory_cache[key]
            self.stats['entries'] = len(self.memory_cache)
            return True
        return False

    def persist_to_disk(self, filename: str = "cache.pkl") -> bool:
        """Persist cache to disk."""
        try:
            cache_file = self.cache_dir / filename
            with open(cache_file, 'wb') as f:
                pickle.dump(self.memory_cache, f)
            return True
        except Exception as e:
            print(f"Error persisting cache: {e}")
            return False

    def load_from_disk(self, filename: str = "cache.pkl") -> bool:
        """Load cache from disk."""
        try:
            cache_file = self.cache_dir / filename
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    self.memory_cache = pickle.load(f)
                self.stats['entries'] = len(self.memory_cache)
                return True
            return False
        except Exception as e:
            print(f"Error loading cache: {e}")
            return False


class CacheDecorator:
    """Decorator for caching function results."""

    def __init__(self, cache_manager: CacheManager, ttl_seconds: int = 3600):
        self.cache_manager = cache_manager
        self.ttl_seconds = ttl_seconds

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            key = self.cache_manager._generate_key(
                func.__name__,
                {'args': args, 'kwargs': kwargs}
            )

            cached_result = self.cache_manager.get(key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            self.cache_manager.set(key, result, self.ttl_seconds)
            return result

        return wrapper


# Global cache manager instance
_cache_manager = None


def get_cache_manager(cache_dir: str = ".cache") -> CacheManager:
    """Get or create global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(cache_dir)
    return _cache_manager


if __name__ == "__main__":
    print("=" * 60)
    print("Cache Manager")
    print("=" * 60)

    manager = CacheManager()

    print("\n1. Basic Caching:")
    print("-" * 60)
    manager.set("user:123", {"name": "John", "email": "john@example.com"}, ttl_seconds=300)
    manager.set("user:456", {"name": "Jane", "email": "jane@example.com"}, ttl_seconds=300)

    print(f"Stored 2 entries")
    print(f"Get user:123: {manager.get('user:123')}")
    print(f"Get user:456: {manager.get('user:456')}")

    print("\n2. Agent Response Caching:")
    print("-" * 60)
    key = manager.cache_agent_response(
        "DataAnalyzer",
        {"dataset": "sales", "operation": "sum"},
        "Total sales: $100,000"
    )
    print(f"Cached response with key: {key}")
    result = manager.get_cached_response(
        "DataAnalyzer",
        {"dataset": "sales", "operation": "sum"}
    )
    print(f"Retrieved: {result}")

    print("\n3. Cache Statistics:")
    print("-" * 60)
    manager.get("user:123")  # Hit
    manager.get("user:789")  # Miss
    info = manager.get_cache_info()
    print(f"Total Entries: {info['total_entries']}")
    print(f"Hits: {info['hits']}")
    print(f"Misses: {info['misses']}")
    print(f"Hit Rate: {info['hit_rate']}")

    print("\n4. Persist to Disk:")
    print("-" * 60)
    success = manager.persist_to_disk("test_cache.pkl")
    print(f"Persisted: {success}")

    print("\n5. Load from Disk:")
    print("-" * 60)
    new_manager = CacheManager()
    loaded = new_manager.load_from_disk("test_cache.pkl")
    print(f"Loaded: {loaded}")
    print(f"Entries: {len(new_manager.memory_cache)}")

    print("\n6. Clear Expired:")
    print("-" * 60)
    manager2 = CacheManager()
    manager2.set("old", "data", ttl_seconds=1)
    import time
    time.sleep(2)
    expired = manager2.clear_expired()
    print(f"Cleared {expired} expired entries")
