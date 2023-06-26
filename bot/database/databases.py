import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import (DB_USER,
                     DB_PASS,
                     DB_HOST,
                     DB_PORT,
                     DB_NAME)


DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:' \
               f'{DB_PORT}/{DB_NAME}'

engine = create_engine(DATABASE_URL)

Session = sessionmaker(engine,
                       autocommit=False,
                       autoflush=False)
session = Session()

def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()


def get_connection():
    """
    Фунция для дальнейшего сырого запроса к
    базе данных (на всякий случай).
    """
    conn = psycopg2.connect(dbname=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS,
                            host=DB_HOST,
                            port=DB_PORT)
    return conn
