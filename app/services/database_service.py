from datetime import datetime, timezone, timedelta
from typing import Type, Optional

from fastapi import Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from core import get_session, Base
from models import URLMetadata, URLCounter


class DatabaseService:
    def __init__(self, session: Session):
        self.session = session

    def find_all(self, base_type: Type[Base], filter_by: Optional[and_] = None):
        query = self.session.query(base_type)
        if filter_by is not None:
            query = query.filter(filter_by)
        return query.all()

    def create_url_counter(self) -> URLCounter:
        url_counter = URLCounter()
        self.session.add(url_counter)
        self.commit_and_refresh(url_counter)
        return url_counter

    def increment_url_counter(self) -> int:
        url_counter = self.session.query(URLCounter).first()
        if not url_counter:
            url_counter = self.create_url_counter()

        url_counter.last_id += 1
        self.commit_and_refresh(url_counter)
        return url_counter.last_id

    def find_by_long_url(self, client_id: str, long_url: str) -> URLMetadata | None:
        expired_time = datetime.now(timezone.utc) - timedelta(days=90)
        return (self.session
                .query(URLMetadata)
                .filter(and_(URLMetadata.client_id == client_id,
                             URLMetadata.long_url == long_url,
                             URLMetadata.created_at > expired_time))
                .first())

    def find_by_short_url(self, short_url: str) -> URLMetadata | None:
        expired_time = datetime.now(timezone.utc) - timedelta(days=90)
        return (self.session
                .query(URLMetadata)
                .filter(and_(URLMetadata.short_url == short_url,
                             URLMetadata.created_at > expired_time))
                .first())

    def add_and_refresh(self, entity: Type[Base]):
        self.session.add(entity)
        self.commit_and_refresh(entity)

    def commit_and_refresh(self, entity: Type[Base]):
        self.session.commit()
        self.session.refresh(entity)


def get_database_service(session: Session = Depends(get_session)) -> DatabaseService:
    return DatabaseService(session)
