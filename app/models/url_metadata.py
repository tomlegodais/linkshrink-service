import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from core import Base


class URLMetadata(Base):
    __tablename__ = 'url_metadata'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(String, index=True, nullable=False)
    long_url = Column(String, index=True, nullable=False)
    short_url = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
