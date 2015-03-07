from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from utils import fredis
from fbase import get_session

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=45))
    session_key = Column(String(length=45))
    register_time = Column(String(length=100))
    is_valid = Column(Integer, default=1)
    has_played = Column(Integer, default=0)


def add_user(username, session_key, register_time):
    session = get_session()
    user = User(username=username, session_key=session_key,
                register_time=register_time)
    session.add(user)
    session.commit()


def add_waiting_user(username):
    '''
    For those users who have not crawled the last.fm, put them
    in the redis
    '''
    fredis.r_cli.sadd(fredis.waiting_user_set, username)


def get_waiting_user():
    '''
    Get user who have not crawled the last.fm randomly
    '''
    return fredis.r_cli.srandmember(fredis.waiting_user_set)


def is_in_waiting_user(username):
    '''
    Check the user whether is the waiting list
    '''
    return fredis.r_cli.sismember(fredis.waiting_user_set, username)


def del_waiting_user(username):
    '''
    Delete user who have not crawled the last.fm
    '''
    fredis.r_cli.srem(fredis.waiting_user_set, username)


def do_exist_user(username):
    '''
    Check wheter user has alredy existed
    '''
    session = get_session()
    return session.query(User).filter(User.username == username).first()


def update_session(username, session_key):
    '''
    Update session for the user
    '''
    session = get_session()
    chosen_user = session.query(User).filter(User.username == username).first()
    chosen_user.session_key = session_key
    session.commit()


def get_session_key(username):
    '''
    Get user's session key
    '''
    db_session = get_session()
    chosen_user = db_session.query(User).filter(User.username == username).\
        first()
    return chosen_user.session_key


def get_all_users():
    '''
    Get all available users
    '''
    session = get_session()
    all_users = session.query(User).filter(User.is_valid == 1).all()
    return all_users
