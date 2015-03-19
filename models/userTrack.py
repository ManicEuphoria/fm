import collections
import uuid

from constants.main import MP3_FILE_PREFIX, WY_ARTIST_PREFIX
from constants.main import WY_ALBUM_PREFIX, WY_SONG_PREFIX
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from utils import fredis, zeus
from constants import redname
from fbase import get_session

Base = declarative_base()

NextTrack = collections.namedtuple("NextTrack", [
    'title', "artist", "url", "is_star", "track_type", "album_url",
    'album_id', "artist_id", "song_id", 'duration'])


class TrackInfo(Base):
    __tablename__ = "trackInfo"
    track_info_id = Column(Integer, primary_key=True, autoincrement=True)
    track_uuid = Column(String(length=100))
    title = Column(String(length=400))
    artist = Column(String(length=200))
    mp3_url = Column(String(length=300))
    album_url = Column(String(length=200))
    album_id = Column(String(length=100))
    artist_id = Column(String(length=100))
    duration = Column(String(length=100))
    emotion_value = Column(Integer)


class UserTrack(Base):
    __tablename__ = "userTrack"
    user_track_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=100))
    track_uuid = Column(String(length=100))
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


def add_tracks_info(final_tracks_list):
    '''
    Add tracks basic info into TrackInfo
    '''
    db_session = get_session()
    for final_track in final_tracks_list:
        added_track = db_session.query(TrackInfo)\
            .filter(TrackInfo.artist == final_track.artist)\
            .filter(TrackInfo.title == final_track.title).first()
        if added_track:
            final_track.track_uuid = added_track.track_uuid
        else:
            track = TrackInfo(track_uuid=final_track.track_uuid,
                              artist=final_track.artist,
                              title=final_track.title)
            db_session.add(track)
    db_session.commit()


def add_tracks_emotion(tracks_list):
    '''
    Add the tracks' emotion to db
    '''
    db_session = get_session()
    tracks_info = dict([(track.track_uuid, track.emotion_value)
                        for track in tracks_list])
    emotion_tracks = db_session.query(TrackInfo)\
        .filter(TrackInfo.track_uuid.in_(tracks_info.keys())).all()
    for emotion_track in emotion_tracks:
        emotion_track.emotion = tracks_info[emotion_track.track_uuid]
    db_session.commit()


def add_rec_tracks(username, rec_tracks):
    '''
    Add the recommendation tracks into database
    '''
    add_tracks_info(rec_tracks)
    db_session = get_session()
    for rec_track in rec_tracks:
        rec_track = RecTrack(username=username,
                             track_uuid=rec_track.track_uuid)
        db_session.add(rec_track)
    db_session.commit()


def add_tracks(username, final_tracks_list):
    '''
    Add user tracks info into UserTrack
    '''
    add_tracks_info(final_tracks_list)
    session = get_session()
    for final_track in final_tracks_list:
        track_uuid = final_track.track_uuid
        level = final_track.level
        is_star = final_track.is_star
        user_track = UserTrack(username=username,
                               track_uuid=track_uuid, level=level,
                               is_star=is_star)
        session.add(user_track)
    session.commit()


def store_tracks_info(user_tracks):
    '''
    Store tracks info like mp3 url
    '''
    db_session = get_session()
    for track in user_tracks:
        track_info = db_session.query(TrackInfo)\
            .filter(TrackInfo.track_uuid == track.track_uuid).first()
        track_info.mp3_url = track.mp3_url
        track_info.album_url = track.album_url
        track_info.album_id = track.album_id
        track_info.aritst_id = track.artist_id
        track_info.duration = track.duration
    db_session.commit()


def choose_tracks_info(all_tracks):
    '''
    Choose all the tracks info like mp3 url
    '''
    db_session = get_session()
    tracks_uuids = [track.track_uuid for track in all_tracks]
    tracks_info = db_session.query(TrackInfo)\
        .filter(TrackInfo.track_uuid.in_(tracks_uuids)).all()
    return tracks_info


def choose_all_tracks(username):
    """
    Choose All tracks from one user
    """
    db_session = get_session()
    all_tracks = db_session.query(UserTrack)\
        .filter(UserTrack.username == username).all()
    return all_tracks


def choose_rec_tracks(username):
    '''
    Choose all recommendation tracsk from user
    '''
    db_session = get_session()
    rec_tracks = db_session.query(RecTrack)\
        .filter(RecTrack.username == username).all()
    return rec_tracks


def get_top_level_tracks(username):
    db_session = get_session()
    all_top_tracks = db_session.query(UserTrack)\
        .filter(UserTrack.username == username)\
        .filter(UserTrack.level == 4).all()
    return all_top_tracks


def set_songs_ids(username, chosen_tracks, radio_type="normal"):
    '''
    Set to-played songs ids into redis
    '''
    for track in chosen_tracks:
        if radio_type == "normal":
            to_play_tracks = "toplay:%s:list" % (username)
        elif radio_type == "emotion":
            to_play_tracks = "emotion:toplay:%s:list" % (username)
        fredis.r_cli.rpush(to_play_tracks, track.track_uuid)


def set_next_playlist(username, next_playlist_track):
    '''
    Set next playlist songs id into redis
    '''
    fredis.r_cli.set(redname.NEXT_PLAYLIST, next_playlist_track)


def del_songs_ids_info(username, radio_type):
    '''
    Delete toplay List and songs info
    '''
    track_uuids = get_all_songs_ids(username, radio_type)
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
        fredis.r_cli.hset(user_track, "album_url", str(track.album_url))
        fredis.r_cli.hset(user_track, "album_id", str(track.album_id))
        fredis.r_cli.hset(user_track, "artist_id", str(track.artist_id))
        fredis.r_cli.hset(user_track, "song_id", str(track.song_id))
        fredis.r_cli.hset(user_track, "duration", str(track.duration))
        try:
            fredis.r_cli.hset(user_track, "type", str(track.type))
            if track.type == "lib":
                fredis.r_cli.hset(user_track, 'is_star', str(track.is_star))
            else:
                fredis.r_cli.hset(user_track, 'is_star', 0)
        except Exception as e:
            print(e)


def get_all_songs_ids(username, radio_type):
    '''
    Get all songs ids in redis
    '''
    if radio_type == "normal":
        to_play_tracks = "toplay:%s:list" % (username)
    elif radio_type == "emotion":
        to_play_tracks = "emotion:toplay:%s:list" % (username)

    tracks_uuids = [fredis.r_cli.lpop(to_play_tracks)
                    for i in xrange(fredis.r_cli.llen(to_play_tracks))]
    print(tracks_uuids)
    return tracks_uuids


def get_next_playlist(username):
    '''
    Get next user's playlist
    '''
    next_track = fredis.r_cli.get(redname.NEXT_PLAYLIST + username)
    return next_track


def get_next_song_id(username, radio_type):
    '''
    Get next songs id
    '''
    if radio_type == "normal":
        to_play_tracks = "toplay:%s:list" % (username)
    elif radio_type == "emotion":
        to_play_tracks = "emotion:toplay:%s:list" % (username)
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


def remain_tracks(username):
    '''
    returns the number of tracks in the user's to-listened tracks
    '''
    to_play_tracks = "toplay:%s:list" % (username)
    return int(fredis.r_cli.llen(to_play_tracks))
