from starlette.requests import Request


def get_ipaddr(request: Request) -> str:
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For']

    if not request.client or not request.client.host:
        return '127.0.0.1'

    return request.client.host
