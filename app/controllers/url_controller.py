from fastapi import APIRouter, Depends, status, HTTPException
from starlette.requests import Request as HttpRequest
from starlette.responses import Response as HttpResponse

from schemas import URLResponse, ShrinkRequest
from services import URLService, get_url_service

router = APIRouter(prefix="/url")


@router.get(path="", response_model=list[URLResponse])
async def find_all(http_request: HttpRequest,
                   url_service: URLService = Depends(get_url_service)) -> list[URLResponse]:
    return url_service.find_all(http_request.state.client_id)


@router.get(path="/{short_url}", response_model=URLResponse)
async def find_by_short_url(http_request: HttpRequest,
                            short_url: str,
                            url_service: URLService = Depends(get_url_service)) -> URLResponse:
    client_id = http_request.state.client_id
    url_response = await url_service.get_long_url(client_id, short_url)
    if not url_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
    return url_response


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
