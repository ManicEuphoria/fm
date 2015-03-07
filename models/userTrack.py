import collections
import uuid

from constants.main import MP3_FILE_PREFIX, WY_ARTIST_PREFIX
from constants.main import WY_ALBUM_PREFIX, WY_SONG_PREFIX
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from utils import fredis
from fbase import get_session

Base = declarative_base()

NextTrack = collections.namedtuple("NextTrack", [
    'title', "artist", "url", "is_star", "track_type", "album_url",
    'album_id', "artist_id", "song_id", 'duration'])


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


class RecTrack(Base):
    __tablename__ = "recTrack"
    user_track_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=100))
    track_uuid = Column(String(length=100))
    title = Column(String(length=400))
    artist = Column(String(length=200))


def add_tracks(username, final_tracks_list):
    session = get_session()
    for number, final_track in enumerate(final_tracks_list):
        track_uuid = final_track.track_uuid
        title = final_track.title
        artist = final_track.artist
        level = final_track.level
        is_star = final_track.is_star
        user_track = UserTrack(username=username, title=title, artist=artist,
                               track_uuid=track_uuid, level=level,
                               is_star=is_star)
        session.add(user_track)
        if number % 200 == 199:
            session.commit()
            session = get_session()
    session.commit()


def choose_all_tracks(username):
    """
    Choose All tracks from one user
    """
    db_session = get_session()
    all_tracks = db_session.query(UserTrack)\
        .filter(UserTrack.username == username).all()
    return all_tracks


def get_top_level_tracks(username):
    db_session = get_session()
    all_top_tracks = db_session.query(UserTrack)\
        .filter(UserTrack.username == username)\
        .filter(UserTrack.level == 4).all()
    return all_top_tracks


def set_songs_ids(username, chosen_tracks):
    '''
    Set to-played songs ids into redis
    '''
    for track in chosen_tracks:
        to_play_tracks = "toplay:%s:list" % (username)
        fredis.r_cli.rpush(to_play_tracks, track.track_uuid)


def del_songs_ids_info(username):
    '''
    Delete toplay List and songs info
    '''
    track_uuids = get_all_songs_ids(username)
    for track_uuid in track_uuids:
        user_track = "%s:trackinfo:%s" % (username, track_uuid)
        fredis.r_cli.delete(user_track)


def is_ready(username):
    '''
    Check whether the user track has put into to-played songs ids in redis
    '''
    to_play_tracks = 'toplay:%s:list' % (username)
    return True if fredis.r_cli.llen(to_play_tracks) > 0 else False


def set_songs_info(username, chosen_tracks):
    '''
    Set songs extra info into redis
    '''
    for track in chosen_tracks:
        track_uuid = track.track_uuid
        user_track = "%s:trackinfo:%s" % (username, track_uuid)
        fredis.r_cli.hset(user_track, "artist", str(track.artist))
        fredis.r_cli.hset(user_track, "title", str(track.title))
        fredis.r_cli.hset(user_track, "url", str(track.mp3_url))
        fredis.r_cli.hset(user_track, "type", str(track.type))
        fredis.r_cli.hset(user_track, "album_url", str(track.album_url))
        fredis.r_cli.hset(user_track, "album_id", str(track.album_id))
        fredis.r_cli.hset(user_track, "artist_id", str(track.artist_id))
        fredis.r_cli.hset(user_track, "song_id", str(track.song_id))
        fredis.r_cli.hset(user_track, "duration", str(track.duration))
        if track.type == "lib":
            fredis.r_cli.hset(user_track, 'is_star', str(track.is_star))
        else:
            fredis.r_cli.hset(user_track, 'is_star', 0)


def get_all_songs_ids(username):
    '''
    Get all songs ids in redis
    '''
    to_play_tracks = "toplay:%s:list" % (username)
    tracks_uuids = [fredis.r_cli.lpop(to_play_tracks)
                    for i in xrange(fredis.r_cli.llen(to_play_tracks))]
    return tracks_uuids


def get_next_song_id(username):
    '''
    Get next songs id
    '''
    to_play_tracks = "toplay:%s:list" % (username)
    track_uuid = fredis.r_cli.lpop(to_play_tracks)
    return track_uuid


def get_next_track(username, track_uuid):
    '''
    Get next track's information
    '''
    user_track = "%s:trackinfo:%s" % (username, track_uuid)
    title = fredis.r_cli.hget(user_track, 'title')
    artist = fredis.r_cli.hget(user_track, 'artist')
    is_star = fredis.r_cli.hget(user_track, 'is_star')
    track_type = fredis.r_cli.hget(user_track, "type")
    url = fredis.r_cli.hget(user_track, 'url')
    url = MP3_FILE_PREFIX + url + '.mp3'
    album_url = fredis.r_cli.hget(user_track, "album_url")
    artist_id = fredis.r_cli.hget(user_track, "artist_id")
    artist_id = WY_ARTIST_PREFIX + artist_id
    album_id = fredis.r_cli.hget(user_track, "album_id")
    album_id = WY_ALBUM_PREFIX + album_id
    song_id = fredis.r_cli.hget(user_track, "song_id")
    song_id = WY_SONG_PREFIX + song_id
    duration = fredis.r_cli.hget(user_track, 'duration')
    track = NextTrack(title, artist, url, is_star, track_type, album_url,
                      album_id, artist_id, song_id, duration)
    fredis.r_cli.delete(user_track)
    return track


def add_rec_tracks(username, rec_tracks):
    '''
    Add the recommendation tracks into database
    '''
    db_session = get_session()
    for rec_track in rec_tracks:
        track_uuid = str(uuid.uuid4())[0: 8]
        rec_track = RecTrack(username=username, track_uuid=track_uuid,
                             title=rec_track.title,
                             artist=str(rec_track.artist))
        db_session.add(rec_track)
    db_session.commit()


def choose_rec_tracks(username):
    '''
    Choose all recommendation tracsk from user
    '''
    db_session = get_session()
    rec_tracks = db_session.query(RecTrack)\
        .filter(RecTrack.username == username).all()
    return rec_tracks


def remain_tracks(username):
    '''
    returns the number of tracks in the user's to-listened tracks
    '''
    to_play_tracks = "toplay:%s:list" % (username)
    return int(fredis.r_cli.llen(to_play_tracks))
