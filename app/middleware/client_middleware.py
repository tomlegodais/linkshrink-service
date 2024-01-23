import hashlib

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from utils import get_ipaddr


def _get_client_id(request: Request) -> str:
    ip_addr = get_ipaddr(request)
    return hashlib.sha256(ip_addr.encode('utf-8')).hexdigest()


class AttachClientMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.client_id = _get_client_id(request)
        return await call_next(request)
