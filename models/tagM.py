from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from utils import fredis
from fbase import get_session

Base = declarative_base()


class EmotionTag(Base):
    __tablename__ = "emotionTrack"
    emotion_track_id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(length=50))
    track_uuid = Column(String(length=20))
    track_type = Column(String(length=10))
    artist = Column(String(length=100))
    title = Column(String(length=200))
    emotion = Column(String(length=10))
    emotion_value = Column(Integer)


def store_emotion(username, emotion_array, track_type):
    '''
    Store emotion in database
    emotion_array df9d13ea
    '''
    db_session = get_session()
    for emotion in emotion_array:
        emotion_tag = EmotionTag(
            track_uuid=emotion.track_uuid,
            username=username,
            track_type=track_type,
            artist=emotion.artist,
            title=emotion.title,
            emotion=emotion.emotion[0],
            emotion_value=emotion.emotion[1])
        db_session.add(emotion_tag)
    db_session.commit()


def get_emotion_tracks(username, emotion):
    '''
    Get all tracks from one emotion
    '''
    db_session = get_session()
    return db_session.query(EmotionTag).\
        filter(EmotionTag.username == username).\
        filter(EmotionTag.emotion == emotion).all()
