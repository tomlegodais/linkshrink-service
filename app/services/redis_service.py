import hashlib

import redis.asyncio as redis

from core import Config
from schemas import URLResponse


class RedisService:
    def __init__(self, expiry_time: int = 30):
        self.redis_client = redis.from_url(f'{Config.REDIS_URL}/1')
        self.expiry_time = expiry_time

    @staticmethod
    def __get_cache_key(client_id: str, url: str) -> str:
        url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
        return f'{client_id}:{url_hash}'

    async def get_url_response(self, client_id: str, url: str) -> URLResponse | None:
        cache_key = self.__get_cache_key(client_id, url)
        serialized_data = await self.redis_client.get(cache_key)
        return URLResponse.model_validate_json(serialized_data) if serialized_data else None

    async def set_url_response(self, client_id: str, key_value: str, url_response: URLResponse) -> None:
        cache_key = self.__get_cache_key(client_id, key_value)
        serialized_data = url_response.model_dump_json()
        await self.redis_client.set(cache_key, serialized_data, ex=self.expiry_time)


redis_service_instance = None


async def get_redis_service():
    global redis_service_instance
    if not redis_service_instance:
        redis_service_instance = RedisService()
    return redis_service_instance
