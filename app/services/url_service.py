import time
from typing import Tuple, Callable

import base58
from fastapi import Depends

from models import URLMetadata
from schemas import URLResponse
from utils import select_random_sampling
from .database_service import DatabaseService, get_database_service
from .redis_service import RedisService, get_redis_service


class URLService:

    def __init__(self, database_service: DatabaseService, redis_service: RedisService):
        self.database_service = database_service
        self.redis_service = redis_service

    def find_all(self, client_id: str) -> list[URLResponse]:
        urls = [URLResponse.model_validate(url) for url in
                self.database_service.find_all(URLMetadata, URLMetadata.client_id == client_id)]

        return sorted(urls, key=lambda url: url.created_at, reverse=True)

    def _create_short_url(self, length: int = 6) -> str:
        counter_id = self.database_service.increment_url_counter()
        unique_bytes = str(int(time.time() * 1000) * counter_id).encode('utf-8')
        base58_encoded = base58.b58encode(unique_bytes).decode('utf-8')
        return select_random_sampling(base58_encoded, length)

    async def _get_and_cache_metadata(self,
                                      client_id: str,
                                      url: str,
                                      database_fn: Callable[[str, str], URLMetadata]) -> URLResponse | None:
        url_metadata = database_fn(client_id, url)
        if url_metadata:
            url_response = URLResponse.model_validate(url_metadata)
            await self.redis_service.set_url_response(client_id, url, url_response)
            return url_response
        return None

    async def create_url_response(self, client_id: str, long_url: str) -> Tuple[URLResponse, bool]:
        url_response = (await self.redis_service.get_url_response(client_id, long_url) or
                        await self._get_and_cache_metadata(client_id, long_url, self.database_service.get_url_metadata))

        if url_response:
            return url_response, False

        short_url = self._create_short_url()
        url_metadata = URLMetadata(client_id=client_id, long_url=long_url, short_url=short_url)
        self.database_service.add_and_refresh(url_metadata)

        url_response = URLResponse.model_validate(url_metadata)
        await self.redis_service.set_url_response(client_id, url_response.long_url, url_response)
        return url_response, True

    async def get_long_url(self, client_id: str, short_url: str) -> URLResponse | None:
        url_response = (await self.redis_service.get_url_response(client_id, short_url) or
                        await self._get_and_cache_metadata(client_id, short_url,
                                                           self.database_service.get_url_metadata))
        return url_response if url_response else None


def get_url_service(database_service: DatabaseService = Depends(get_database_service),
                    redis_service: RedisService = Depends(get_redis_service)) -> URLService:
    return URLService(database_service, redis_service)
