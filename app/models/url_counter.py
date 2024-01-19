from sqlalchemy import Column, Integer

from core import Base


class URLCounter(Base):
    __tablename__ = 'url_counter'

    id = Column(Integer, primary_key=True, index=True)
    last_id = Column(Integer, nullable=False, default=0)
