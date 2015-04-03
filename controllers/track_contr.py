import json

from models import userTrack
from utils.picker import Picker, EmotionPicker
from constants import redname, main
from constants.main import STORED_TRACKS_NUMBER, STORED_EMOTION_NUMBER
from utils import fredis, zeus, picker


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


def get_next_song(username, radio_type,
                  lib_ratio=None, emotion_range=None, track_number=None,
                  reverse_type=None, last_tag=None, tag_value=None,
                  last_emotion_value=None):
    '''
    Get the url and extra info about the next song
    If there are more than one song ,return the list
    If there is only one song ,return the track it self

    reverse_type is whether lib/rec reverse
    '''
    if radio_type == "pre":
        track_uuid = userTrack.get_next_pre_track(username)
        to_play_track = userTrack.get_one_track_detail(track_uuid)
        to_play_track = get_track_info(username, to_play_track, 'lib')
        return to_play_track
    elif radio_type == "normal":
        track_picker = picker.Picker(username, emotion_range)
        to_play_track = track_picker.next_mix(track_number, lib_ratio,
                                              reverse_type, last_tag,
                                              tag_value, last_emotion_value)
        to_play_track = get_track_info(username, to_play_track,
                                       to_play_track.type)
        print(to_play_track.title)
        print(to_play_track.artist)
        print('emotion_value is %s' % (to_play_track.emotion_value))
        print('tag is %s value %s ' % (to_play_track.tag,
                                       to_play_track.tag_value))
        print("track type is %s" % (to_play_track.type))
        return to_play_track


def next_status(lib_ratio, emotion_range, track_number, last_track, last_type,
                last_tag, tag_value):
    '''
    Get next track's status according to the last track
    1. Switch the track or not
    '''
    # @todo (the lib ratio should be adjusted slightly)

    reverse_type = None
    switch_track_number = [2, 3, ]
    not_switch_track_number = [1]
    if not last_track and (track_number == 0 or
                           (track_number in switch_track_number and
                            last_type == "lib") or
                           track_number == 4):
        # Switch the emotion
        track_number = 0
        emotion_range = zeus.next_jump_emotion(emotion_range)
        tag_value = None

    elif not last_track and (track_number in not_switch_track_number or
                             (track_number in switch_track_number and
                              last_type == "rec")):
        # Not switch the emotion , next track in the track list but
        # change the lib ratio
        track_number += 1
        # if last_type == "lib" and not lib_ratio == 20:
        #     lib_ratio -= 20
        #     reverse_type = 'rec'
        # elif last_type == "rec" and not lib_ratio == 100:
        #     lib_ratio += 20
        #     reverse_type = "lib"

    elif last_track and track_number == 4:
        # The last track in the track list
        track_number = 0
        emotion_range = zeus.next_list_emotion(emotion_range)
        tag_value = None
    elif last_track:
        # The next track in original track list
        track_number += 1
    return [lib_ratio, emotion_range, track_number, reverse_type,
            last_tag, tag_value]


def get_track_info(username, to_play_track, track_type):
    '''
    From the track uuid , get the mp3 url info first , then get the
    level and is_star if track type is lib
    '''
    if track_type == "lib":
        level, is_star = userTrack.get_personal_track_info(
            username, to_play_track.track_uuid)
        to_play_track.level = level
        to_play_track.is_star = is_star
    elif track_type == "rec":
        to_play_track.is_star = "0"
    return to_play_track


def get_next_playlist(username, lib_ratio, emotion_range):
    '''
    (# Depre)Get next playlist first track, and update next tracks list
    '''
    next_track = userTrack.get_next_playlist(username)
    refresh_msg = {
        "username": username,
        "lib_ratio": lib_ratio,
        "emotion_range": emotion_range
    }
    fredis.r_cli.publish(redname.PLAYLIST_REFRESH, json.dumps(refresh_msg))
    # refresh.py to refresh the this playlist track
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
