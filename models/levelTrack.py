import collections

from constants.main import MP3_FILE_PREFIX
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from utils import fredis
from fbase import get_session

Base = declarative_base()

NextTrack = collections.namedtuple("NextTrack", [
    'title', "artist", "url", "is_star"])


class UserTrack(Base):
    __tablename__ = "userTrack"
    user_track_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=100))
    track_uuid = Column(String(length=100))
    title = Column(String(length=400))
    artist = Column(String(length=200))
    level = Column(Integer)
    is_star = Column(Integer)

    def __repr__(self):
        return "title %s artist %s level %s is_star %s" % (
            self.title, self.artist, self.level, self.is_star)


def add_tracks(username, final_tracks_list):
    session = get_session()
    for final_track in final_tracks_list:
        track_uuid = final_track.track_uuid
        title = final_track.title
        artist = final_track.artist
        level = final_track.level
        is_star = final_track.is_star
        user_track = UserTrack(username=username, title=title, artist=artist,
                               track_uuid=track_uuid, level=level,
                               is_star=is_star)
        session.add(user_track)
    session.commit()


def choose_all_tracks(username):
    """
    Choose All tracks from one user
    """
    db_session = get_session()
    all_tracks = db_session.query(UserTrack)\
        .filter(UserTrack.username == username).all()
    return all_tracks


def set_songs_ids(username, chosen_tracks):
    '''
    Set to-played songs ids into redis
    '''
    for track in chosen_tracks:
        to_play_tracks = "toplay:%s:list" % (username)
        fredis.r_cli.rpush(to_play_tracks, track.track_uuid)
        print(track.title, track.level)


def set_songs_info(username, chosen_tracks):
    '''
    Set songs extra info into redis
    '''
    for track in chosen_tracks:
        track_uuid = track.track_uuid
        user_track = "%s:trackinfo:%s" % (username, track_uuid)
        fredis.r_cli.hset(user_track, 'is_star', str(track.is_star))
        fredis.r_cli.hset(user_track, "artist", str(track.artist))
        fredis.r_cli.hset(user_track, "title", str(track.title))
        fredis.r_cli.hset(user_track, "url", str(track.mp3_url))


def get_next_song_id(username):
    '''
    Get next songs id
    '''
    to_play_tracks = "toplay:%s:list" % (username)
    track_uuid = fredis.r_cli.lpop(to_play_tracks)
    print(track_uuid)
    return track_uuid


def get_next_track(username, track_uuid):
    '''
    Get next track's information
    '''
    user_track = "%s:trackinfo:%s" % (username, track_uuid)
    title = fredis.r_cli.hget(user_track, 'title')
    artist = fredis.r_cli.hget(user_track, 'artist')
    is_star = fredis.r_cli.hget(user_track, 'is_star')
    url = fredis.r_cli.hget(user_track, 'url')
    url = MP3_FILE_PREFIX + url + '.mp3'
    track = NextTrack(title, artist, url, is_star)
    fredis.r_cli.delete(user_track)
    return track
