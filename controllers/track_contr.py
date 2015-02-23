from models import userTrack
from utils.picker import Picker
from constants.main import STORED_TRACKS_NUMBER


def choose_tracks(username):
    '''
    Choose all user tracks from database
    And pick some tracks
    '''
    tracks_list = userTrack.choose_all_tracks(username)
    picker = Picker(tracks_list, username)
    tracks_list = [picker.next_lib()
                   for i in xrange(STORED_TRACKS_NUMBER)]
    return tracks_list


def filter_no_tracks(chosen_tracks):
    '''
    Filter those track which have no mp3 urls
    '''
    chosen_tracks = [track for track in chosen_tracks
                     if track.mp3_url]
    return chosen_tracks


def store_urls(username, chosen_tracks):
    '''
    Store the mp3 urls into redis
    '''
    userTrack.set_songs_ids(username, chosen_tracks)
    userTrack.set_songs_info(username, chosen_tracks)


def get_next_song(username):
    '''
    Get the url and extra info about the next song
    '''
    track_uuid = userTrack.get_next_song_id(username)
    track = userTrack.get_next_track(username, track_uuid)
    return track
