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
    neighbours = user.get_neighbours(limit=50)
    return neighbours


def get_neighbours_fav(user, progress):
    '''
    Get one neighbour user's favourite tracks
    '''
    top_tracks = user.get_top_tracks(limit=500)
    print(progress)
    return top_tracks
