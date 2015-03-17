import random
from constants import main
from constants.main import MAX_PAST_ARTISTS, LEVELS_ORDER, MAX_PAST_TRACKS
from constants.main import MAX_PAST_EMOTION_ARTISTS, MAX_PAST_EMOTION_TRACKS
from constants.main import EMOTION_ORDER

from utils import fredis

LIB_RATIO = 75


class FixedLengthList(object):
    def __init__(self, length, username, limit_name):
        self.length = length
        self.key_name = "%slimit:%s" % (limit_name, username)

    def append(self, item):
        if fredis.r_cli.llen(self.key_name) >= self.length:
            fredis.r_cli.lpop(self.key_name)
        fredis.r_cli.rpush(self.key_name, item)

    def exist(self, item):
        '''
        Check whether the item is in the list
        '''
        items_in_list = fredis.r_cli.lrange(self.key_name, 0, -1)
        return True if item in items_in_list else False


class EmotionPicker(object):
    def __init__(self, username, emotion, emotion_tracks):
        self.username = username
        self.emotion = emotion
        self.emotion_tracks = emotion_tracks
        self.past_artists = FixedLengthList(MAX_PAST_EMOTION_ARTISTS, username,
                                            'artists')
        self.past_tracks = FixedLengthList(MAX_PAST_EMOTION_TRACKS, username,
                                           'tracks')
        self.choice_pos = 0

    def next_track(self):
        while 1:
            random.shuffle(self.emotion_tracks)
            chosen_track = random.choice(self.emotion_tracks)
            if not self.past_artists.exist(chosen_track.artist) and \
                    not self.past_tracks.exist(chosen_track.title) and \
                    self.in_choice(chosen_track):
                break
        self.past_artists.append(chosen_track.artist)
        self.past_tracks.append(chosen_track.title)
        self.next_choice()
        return chosen_track

    def in_choice(self, chosen_track):
        lib_rec = EMOTION_ORDER[self.choice_pos]['type']
        min_value = EMOTION_ORDER[self.choice_pos]['min']
        max_value = EMOTION_ORDER[self.choice_pos]['max']
        if lib_rec == chosen_track.track_type and\
                min_value < chosen_track.emotion_value < max_value:
            return True
        else:
            return False

    def next_choice(self):
        if self.choice_pos == (len(EMOTION_ORDER) - 1):
            self.choice_pos = 0
        else:
            self.choice_pos += 1


class Picker(object):
    def __init__(self, lib_list, rec_list, username, emotion_range):
        self.lib_list = lib_list
        self.rec_list = rec_list
        self.past_artists = FixedLengthList(MAX_PAST_ARTISTS, username,
                                            "artists")
        self.past_tracks = FixedLengthList(MAX_PAST_TRACKS, username,
                                           "tracks")
        self.emotion_range = emotion_range
        self.pick_pos = 0

    def _next_level_pos(self):
        '''
        Next position in the levels orders
        '''
        if self.pick_pos == (len(LEVELS_ORDER) - 1):
            self.pick_pos = 0
        else:
            self.pick_pos += 1

    def next_mix(self, track_number, lib_ratio):
        '''
        Pick one song either from libarary or recommendation
        Depends on the LIB_RATIO
        '''
        is_lib = main.IS_LIB[lib_ratio][track_number]
        if is_lib:
            return self.next_lib()
        else:
            return self.next_rec()

    def next_rec(self, track_number):
        '''
        Choose next track from the user's recommendation
        '''
        emo_range = main.emotion_range_add(self.emotion_ratio,
                                           track_number)
        next_tracks = [emotion_track for emotion_track in self.rec_list
                       if emo_range[0] <= emotion_track.emotion_value <=
                       emo_range[1]]

        while 1:
            next_track = random.choice(next_tracks)
            if not self.past_artists.exist(next_track.artist):
                break
        self.past_artists.append(next_track.artist)
        next_track.type = "rec"
        return next_track

    def next_lib(self, track_number):
        '''
        Choose next track from the user's own library
        '''
        emo_range = main.emotion_range_add(self.emotion_ratio,
                                           track_number)
        emotion_tracks = [emotion_track for emotion_track in self.lib_list
                          if emo_range[0] <= emotion_track.emotion_value <=
                          emo_range[1]]
        random.shuffle(emotion_tracks)
        random_track = random.choice(emotion_tracks)
        while 1:
            random_track = random.choice(emotion_tracks)
            if not self.past_artists.exist(random_track.artist) and\
                    not self.past_tracks.exist(random_track.track_uuid):
                break

        # If in the level which can not satisy both rules,pick one
        # randomly from all tracks
        if not emotion_tracks:
            random_track = random.choice(emotion_tracks)

        self.past_tracks.append(random_track.track_uuid)
        self.past_artists.append(random_track.artist)
        random_track.type = "lib"
        return random_track
