from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from fbase import get_session

Base = declarative_base()


class Track(Base):
    __tablename__ = "track"
    track_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(length=400))
    artist = Column(String(length=200))


def add_tracks(tracks):
    '''
    Add track list into database if not exist
    Return the list contains the instances of class TempTrack
    '''
    db_session = get_session()
    result_tracks = []
    for track in tracks:
        title = track.title
        artist = track.artist
        track_in_db = db_session.query(Track)\
            .filter(Track.title == title).filter(Track.artist == artist)\
            .first()
        if track_in_db:
            track.track_id = track_in_db.track_id
        else:
            new_track = Track(title=title, artist=artist)
            track.track_id = new_track.track_id
            db_session.add(new_track)

        result_tracks.append(track)
    db_session.commit()
    return result_tracks
