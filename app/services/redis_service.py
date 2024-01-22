import hashlib

import redis.asyncio as redis

from core import Config
from schemas import URLResponse


class RedisService:
    def __init__(self, expiry_time: int = 30):
        self.redis_client = redis.from_url(f'{Config.REDIS_URL}/1')
        self.expiry_time = expiry_time

    @staticmethod
    def __get_cache_key(url: str, client_id: str = None) -> str:
        url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
        cache_key = url_hash
        if client_id:
            cache_key = f'{client_id}:{cache_key}'
        return cache_key

    async def get_url_response(self, url: str, client_id: str = None) -> URLResponse | None:
        cache_key = self.__get_cache_key(url, client_id)
        serialized_data = await self.redis_client.get(cache_key)
        return URLResponse.model_validate_json(serialized_data) if serialized_data else None

    async def set_url_response(self, key_value: str, url_response: URLResponse, client_id: str = None) -> None:
        cache_key = self.__get_cache_key(key_value, client_id)
        serialized_data = url_response.model_dump_json()
        await self.redis_client.set(cache_key, serialized_data, ex=self.expiry_time)


redis_service_instance = None


async def get_redis_service():
    global redis_service_instance
    if not redis_service_instance:
        redis_service_instance = RedisService()
    return redis_service_instance
