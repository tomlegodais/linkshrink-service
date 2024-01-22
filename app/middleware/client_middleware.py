import hashlib

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


def _get_client_id(request: Request) -> str:
    client_host = request.headers.get('X-Forwarded-For')
    if not client_host:
        client_host = request.client.host

    return hashlib.sha256(client_host.encode('utf-8')).hexdigest()


class AttachClientMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.client_id = _get_client_id(request)
        return await call_next(request)
