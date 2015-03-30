import time

from constants.main import API_KEY, API_SECRET
from models import userM
from utils import pylast


def get_network():
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
    return network


def get_username(session_key):
    network = get_network()
    network.session_key = session_key
    user = str(network.get_authenticated_user())
    return user


def get_user(username, session_key=None):
    network = get_network()
    user = network.get_user(username)
    if session_key:
        network.session_key = session_key
        user = network.get_authenticated_user()
    return user


def get_top_tracks(task_page, progress, user):
    '''
    Get all top tracks in all history
    '''
    tracks = user.get_top_tracks(limit=200, page=task_page)
    return tracks


def get_recent_tracks(task_page, progress, user):
    '''
    Get all top tracks in recent one year
    '''
    tracks = user.get_top_tracks(limit=100, page=task_page,
                                 period=pylast.PERIOD_12MONTHS)
    return tracks


def get_loved_tracks(task_page, progress, user):
    '''
    Get all time love tracks
    '''
    tracks = user.get_loved_tracks(page=task_page)
    return tracks


def get_all_top_tracks(task_number, progress, username):
    user = get_user(username)
    result = user.get_top_tracks(limit=200, page=task_number)
    return result


def get_playcount(username):
    user = get_user(username)
    result = user.get_playcount()
    return int(result)


def get_neighbours(username):
    '''
    Get user's most similar taste who share with
    '''
    user = get_user(username)
    neighbours = user.get_neighbours(limit=70)
    return neighbours


def get_rec_artists(username):
    '''
    Get user's recommendation artists from lastfm
    '''
    session_key = userM.get_session_key(username)
    user = get_user(username, session_key=session_key)
    rec_artists = user.get_recommended_artists(limit=100)
    return rec_artists


def get_artist_top_tracks(artist, progress):
    '''
    Get artist top tracks
    '''
    tracks = artist.get_top_tracks(limit=20)
    print(progress)
    return tracks


def get_neighbours_fav(user_page, progress):
    '''
    user_page is a list contains [user, page_number]
    Get one neighbour user's favourite tracks
    '''
    user = user_page[0]
    page = user_page[1]
    top_tracks = user.get_top_tracks(limit=200, page=page)
    return top_tracks


def scrobble(username, last_track):
    '''
    Scrobble one user, and update playing song
    '''
    try:
        network = get_network()
        session_key = userM.get_session_key(username)
        network.session_key = session_key
        info = last_track.split('||')
        timestamp = int(time.time() - float(info[2]))
        network.scrobble(artist=info[0], title=info[1][1: -1],
                         timestamp=timestamp)
    except:
        pass


def update_playing(username, this_track):
    # @todo(try except)
    try:
        network = get_network()
        network.session_key = userM.get_session_key(username)
        network.update_now_playing(artist=this_track.artist,
                                   title=this_track.title)
    except:
        pass


def get_similar_tracks(user_track, progress):
    network = get_network()
    start_track = pylast.Track(user_track.artist, user_track.title, network)
    tracks = start_track.get_similar(limit=20)
    return tracks


def token_to_session(access_token):
    '''
    Convert user's access_token into session in last.fm
    '''
    network = get_network()
    sg = pylast.SessionKeyGenerator(network)
    session_key = sg.get_web_auth_session_key(access_token)
    return session_key


def loved_track(username, info):
    '''
    When a user love a track
    '''
    network = get_network()
    network.session_key = userM.get_session_key(username)
    track = info.split("||")
    pylast.Track(track[0], track[1][1: -1], network).love()
    # hack @todo


def unloved_track(username, info):
    '''
    When a user fucks the track
    '''
    network = get_network()
    network.session_key = userM.get_session_key(username)
    track = info.split("||")
    pylast.Track(track[0], track[1][1: -1], network).unlove()


def get_top_tags(track):
    '''
    Get this track's top tags
    Track
    user_track_id  username
    track_uuid title artist level is_star
    '''
    network = get_network()
    user_track = pylast.Track(track.artist, track.title, network)
    return user_track.get_top_tags()
