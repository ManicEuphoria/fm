import json

from models import userTrack
from utils.picker import Picker, EmotionPicker
from constants import redname, main
from constants.main import STORED_TRACKS_NUMBER, STORED_EMOTION_NUMBER
from utils import fredis, zeus


def choose_init_tracks(username):
    '''
    Pick for the user initialization
    '''
    lib_list = userTrack.choose_all_tracks(username)
    lib_list = userTrack.choose_tracks_info(lib_list)
    picker = Picker(lib_list, None, username, None)
    tracks_list = [picker.next_init_lib()
                   for i in xrange(10)]
    return tracks_list


def choose_tracks(username, lib_ratio, emotion_range):
    '''
    Choose all user tracks from database
    And pick some tracks
    '''
    lib_list = userTrack.choose_all_tracks(username)
    lib_list = userTrack.choose_tracks_info(lib_list)

    rec_list = userTrack.choose_rec_tracks(username)
    rec_list = userTrack.choose_tracks_info(rec_list)

    picker = Picker(lib_list, rec_list, username, emotion_range)
    tracks_list = [picker.next_mix(track_number, lib_ratio)
                   for track_number in xrange(STORED_TRACKS_NUMBER)]
    next_emotion_range = _next_emotion(emotion_range)
    picker.emotion_range = next_emotion_range
    next_playlist = picker.next_mix(0, lib_ratio)
    return tracks_list, next_playlist


def _next_emotion(emotion_range):
    '''
    Next emotion range
    '''
    if emotion_range[0] != 0 and emotion_range[1] != 400:
        added_value = zeus.choice([-main.EMOTION_ADDED_VALUE,
                                   +main.EMOTION_ADDED_VALUE])
    elif emotion_range[0] == 0:
        added_value = main.EMOTION_ADDED_VALUE
    elif emotion_range[1] == 400:
        added_value = - main.EMOTION_ADDED_VALUE

    next_emotion_range = [None, None]
    next_emotion_range[0] = emotion_range[0] + added_value
    next_emotion_range[1] = emotion_range[1] + added_value
    return next_emotion_range


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


def store_urls(username, chosen_tracks, erase=False, radio_type="normal",
               next_playlist_track=None):
    '''
    First delete past redis info,the store the mp3 urls into redis
    '''
    if erase:
        userTrack.del_songs_ids_info(username, radio_type)
    if radio_type == "normal" and next_playlist_track:
        userTrack.set_songs_ids(username, chosen_tracks)
        userTrack.set_next_playlist(username, next_playlist_track)
    elif radio_type == "emotion":
        userTrack.set_songs_ids(username, chosen_tracks, radio_type=radio_type)
    if next_playlist_track:
        chosen_tracks.append(next_playlist_track)
    userTrack.set_songs_info(username, chosen_tracks)


def get_next_song(username, radio_type, number=1,):
    '''
    Get the url and extra info about the next song
    If there are more than one song ,return the list
    If there is only one song ,return the track it self
    '''
    tracks = []
    for i in xrange(number):
        track_uuid = userTrack.get_next_song_id(username, radio_type)
        track = userTrack.get_next_track(username, track_uuid)
        tracks.append(track)
    return tracks[0] if number == 1 else tracks


def get_next_playlist(username, lib_ratio, emotion_range):
    '''
    Get next playlist first track, and update next tracks list
    '''
    next_track = userTrack.get_next_playlist(username)
    refresh_msg = {
        "username": username,
        "lib_ratio": lib_ratio,
        "emotion_range": emotion_range
    }
    fredis.r_cli.publish(redname.PLAYLIST_REFRESH, json.dumps(refresh_msg))
    return next_track


def get_user_top_tracks(username):
    '''
    Get user's top tracks, every artist's track is limited to
    a certian number
    '''
    tracks_list = userTrack.get_top_level_tracks(username)
    tracks_list = userTrack.choose_tracks_info(tracks_list)
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
