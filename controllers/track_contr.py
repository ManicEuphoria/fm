from models import levelTrack
from models.levelTrack import add_tracks, choose_all_tracks
from utils.picker import Picker
from constants.main import STORED_TRACKS_NUMBER


def add_track_level(username, final_track_list):
    add_tracks(username, final_track_list)


def choose_tracks(username):
    '''
    Choose all user tracks from database
    And pick some tracks
    '''
    tracks_list = choose_all_tracks(username)
    picker = Picker(tracks_list)
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
    levelTrack.set_songs_ids(username, chosen_tracks)
    levelTrack.set_songs_info(username, chosen_tracks)


def get_next_song(username):
    '''
    Get the url and extra info about the next song
    '''
    track_uuid = levelTrack.get_next_song_id(username)
    track = levelTrack.get_next_track(username, track_uuid)
    return track
