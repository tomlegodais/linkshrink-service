from fastapi import APIRouter, Depends, Query, status
from starlette.requests import Request as HttpRequest
from starlette.responses import Response as HttpResponse, RedirectResponse

from schemas import URLResponse, ShrinkRequest
from services import URLService, get_url_service

router = APIRouter(prefix="/url")


@router.get(path="", response_model=list[URLResponse])
async def find_all(http_request: HttpRequest,
                   url_service: URLService = Depends(get_url_service)) -> list[URLResponse]:
    return url_service.find_all(http_request.state.client_id)


@router.get(path="/redirect", response_model=None)
async def redirect(http_request: HttpRequest,
                   short_url: str = Query(..., min_length=6, max_length=6),
                   url_service: URLService = Depends(get_url_service)):
    client_id = http_request.state.client_id
    url_response = await url_service.get_long_url(client_id, short_url)
    if not url_response:
        return HttpResponse(status_code=status.HTTP_404_NOT_FOUND)
    return RedirectResponse(url=url_response.long_url)


@router.post("/shrink", response_model=URLResponse)
async def shrink_url(
        response: HttpResponse,
        http_request: HttpRequest,
        shrink_request: ShrinkRequest,
        url_service: URLService = Depends(get_url_service)) -> URLResponse:
    client_id = http_request.state.client_id
    long_url = str(shrink_request.long_url)
    (url_response, created) = await url_service.create_url_response(client_id, long_url)

    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return url_response
