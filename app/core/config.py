import os


class Config:
    POSTGRES_URL = os.getenv('POSTGRES_URL')
    REDIS_URL = os.getenv('REDIS_URL')
