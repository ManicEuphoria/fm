from models import userTrack
from utils.picker import Picker, EmotionPicker
from constants.main import STORED_TRACKS_NUMBER, STORED_EMOTION_NUMBER


def choose_init_tracks(username):
    '''
    Pick for the user initialization
    '''
    lib_list = userTrack.choose_all_tracks(username)
    picker = Picker(lib_list, None, username)
    tracks_list = [picker.next_lib()
                   for i in xrange(10)]
    return tracks_list


def choose_tracks(username, lib_ratio, emotion_range):
    '''
    Choose all user tracks from database
    And pick some tracks
    '''
    lib_list = userTrack.choose_all_tracks(username)
    rec_list = userTrack.choose_rec_tracks(username)
    picker = Picker(lib_list, rec_list, username, emotion_range)
    tracks_list = [picker.next_mix(track_number, lib_ratio)
                   for track_number in xrange(STORED_TRACKS_NUMBER)]
    return tracks_list


def choose_emotion_tracks(username, emotion_tracks, emotion):
    '''
    Choose all user next emotion tracks
    '''
    picker = EmotionPicker(username, emotion, emotion_tracks)
    tracks_list = [picker.next_track()
                   for i in xrange(STORED_EMOTION_NUMBER)]
    return tracks_list


def filter_no_tracks(chosen_tracks):
    '''
    Filter those track which have no mp3 urls
    '''
    chosen_tracks = [track for track in chosen_tracks
                     if track.mp3_url]
    return chosen_tracks


def store_urls(username, chosen_tracks, erase=False, radio_type="normal"):
    '''
    First delete past redis info,the store the mp3 urls into redis
    '''
    if erase:
        userTrack.del_songs_ids_info(username, radio_type)
    if radio_type == "normal":
        userTrack.set_songs_ids(username, chosen_tracks)
    elif radio_type == "emotion":
        userTrack.set_songs_ids(username, chosen_tracks, radio_type=radio_type)
    userTrack.set_songs_info(username, chosen_tracks)


def get_next_song(username, radio_type, number=1,):
    '''
    Get the url and extra info about the next song
    If there are more than one song ,return the list
    If there is only one song ,return the track it self
    '''
    print(radio_type)
    tracks = []
    for i in xrange(number):
        track_uuid = userTrack.get_next_song_id(username, radio_type)
        track = userTrack.get_next_track(username, track_uuid)
        tracks.append(track)
    return tracks[0] if number == 1 else tracks


def get_user_top_tracks(username):
    '''
    Get user's top tracks, every artist's track is limited to
    a certian number
    '''
    tracks_list = userTrack.get_top_level_tracks(username)
    final_tracks = []
    artists_frequency = {}
    for track in tracks_list:
        if artists_frequency.get(track.artist, 0) <= 6:
            frequency = artists_frequency.get(track.artist, 0) + 1
            artists_frequency[track.artist] = frequency
            final_tracks.append(track)
        if len(final_tracks) >= 700:
            break
    print(len(final_tracks))
    return final_tracks


def is_ready(username):
    '''
    Check whether user has track list in the redis
    '''
    return userTrack.is_ready(username)
