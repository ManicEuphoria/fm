import time

from constants.main import API_KEY, API_SECRET
from utils import pylast


def get_network():
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
    return network


def get_user(username):
    network = get_network()
    user = network.get_user(username)
    return user


def get_top_tracks(task_page, progress, user):
    '''
    Get all top tracks in all history
    '''
    tracks = user.get_top_tracks(limit=200, page=task_page)
    print(progress)
    return tracks


def get_recent_tracks(task_page, progress, user):
    '''
    Get all top tracks in recent one year
    '''
    tracks = user.get_top_tracks(limit=100, page=task_page,
                                 period=pylast.PERIOD_12MONTHS)
    print(progress)
    return tracks


def get_loved_tracks(task_page, progress, user):
    '''
    Get all time love tracks
    '''
    tracks = user.get_loved_tracks(page=task_page)
    return tracks


def extra_info(track, progress, username):
    network = get_network()
    # user = get_user(username)
    # lib = pylast.Library(user, network)
    # lib.get_tracks(track.artist)
    album = pylast.Track(artist='Death Cab for Cutie',
                         title='You Are a Tourist',
                         network=network).get_album()
    # content = lib.get_tracks("Dustin O'Halloran")
    print(album)


def get_all_top_tracks(task_number, progress, username):
    user = get_user(username)
    result = user.get_top_tracks(limit=200, page=task_number)
    print(progress)
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


def get_neighbours_fav(user_page, progress):
    '''
    user_page is a list contains [user, page_number]
    Get one neighbour user's favourite tracks
    '''
    user = user_page[0]
    page = user_page[1]
    top_tracks = user.get_top_tracks(limit=200, page=page)
    print(progress)
    return top_tracks


def scrobble(username, last_track):
    '''
    Scrobble one user, and update playing song
    '''
    network = get_network()
    network.session_key = '1a91ae8be6dcc41774b952cb14246275'
    info = last_track.split('||')
    timestamp = int(time.time() - float(info[2]))
    network.scrobble(artist=info[0], title=info[1], timestamp=timestamp)


def update_playing(username, this_track):
    network = get_network()
    network.session_key = '1a91ae8be6dcc41774b952cb14246275'
    info = this_track.split("||")
    network.update_now_playing(artist=info[0], title=info[1])
