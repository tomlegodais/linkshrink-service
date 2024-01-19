from pydantic import BaseModel, HttpUrl


class ShrinkRequest(BaseModel):
    long_url: HttpUrl
