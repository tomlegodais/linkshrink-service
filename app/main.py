from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_ipaddr
from starlette.middleware.cors import CORSMiddleware

from controllers import root_router, url_router
from core import Config
from middleware import AttachClientMiddleware

limiter = Limiter(key_func=get_ipaddr,
                  default_limits=["10/minute"],
                  storage_uri=f'{Config.REDIS_URL}/0')

app = FastAPI()
app.state.limiter = limiter

app.include_router(root_router, prefix='/v1')
app.include_router(url_router, prefix='/v1')

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware,
                   allow_origins=['*'],
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'])

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(AttachClientMiddleware)
