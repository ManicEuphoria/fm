import random

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from utils import fredis
from fbase import get_session


Base = declarative_base()


class Background(Base):
    __tablename__ = "background"
    background_id = Column(Integer, primary_key=True, autoincrement=True)
    background_url = Column(String(length=200))


def get_random():
    '''
    Get random background
    '''
    db_session = get_session()
    random_row = random.randrange(0, db_session.query(Background).count())
    background = db_session.query(Background)[random_row]
    background_url = background.background_url
    print(background_url)
    return background_url
