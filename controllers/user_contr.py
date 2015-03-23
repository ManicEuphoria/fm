from models import userM
from datetime import datetime


def add_user(username, session_key):
    now_time = datetime.now()
    userM.add_user(username, session_key, now_time)


def add_waiting_user(username):
    '''
    For those users who have not crawled the last.fm, put them
    in the redis
    '''
    userM.add_waiting_user(username)
