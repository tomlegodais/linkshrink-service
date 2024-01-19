from datetime import datetime

from pydantic import BaseModel


class URLResponse(BaseModel):
    short_url: str
    long_url: str
    created_at: datetime

    class Config:
        from_attributes = True
