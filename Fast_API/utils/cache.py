from Fast_API.settings import Settings
from aiocache import caches
from .logger import loggers

settings = Settings()


caches.set_config(
    {
        "default": {
            "cache": "aiocache.SimpleMemoryCache",
            "serializer": {"class": "aiocache.serializers.PickleSerializer"},
        },
        "redis": {
            "cache": "aiocache.RedisCache",
            "endpoint": settings.redis_host,
            "password": settings.redis_password,
            "db": settings.redis_cache_db,
            "timeout": 5,
            "serializer": {"class": "aiocache.serializers.PickleSerializer"},
        },
    }
)
cache = (
    caches.get("default") if not settings.redis_cache_enabled else caches.get("redis")
)

loggers["info"].info(f"Selected cache: {cache}")
