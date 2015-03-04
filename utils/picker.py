import random
from constants.main import MAX_PAST_ARTISTS, LEVELS_ORDER, MAX_PAST_TRACKS
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


class Picker(object):
    def __init__(self, lib_list, rec_list, username):
        self.lib_list = lib_list
        self.rec_list = rec_list
        self.past_artists = FixedLengthList(MAX_PAST_ARTISTS, username,
                                            "artists")
        self.past_tracks = FixedLengthList(MAX_PAST_TRACKS, username,
                                           "tracks")
        self.pick_pos = 0

    def _next_level_pos(self):
        '''
        Next position in the levels orders
        '''
        if self.pick_pos == (len(LEVELS_ORDER) - 1):
            self.pick_pos = 0
        else:
            self.pick_pos += 1

    def next_mix(self):
        '''
        Pick one song either from libarary or recommendation
        Depends on the LIB_RATIO
        '''
        lib_range = xrange(LIB_RATIO)
        random_value = random.choice(xrange(100))
        if random_value in lib_range:
            return self.next_lib()
        else:
            return self.next_rec()

    def next_rec(self):
        '''
        Choose next track from the user's recommendation
        '''
        next_tracks = [track for track in self.rec_list]
        while 1:
            next_track = random.choice(next_tracks)
            if not self.past_artists.exist(next_track.artist):
                break
        self.past_artists.append(next_track.artist)
        next_track.type = "rec"
        return next_track

    def next_lib(self):
        '''
        Choose next track from the user's own library
        '''
        level = LEVELS_ORDER[self.pick_pos]
        self._next_level_pos()
        level_tracks = [track for track in self.lib_list
                        if track.level == level]
        random_track = random.choice(level_tracks)
        while 1:
            random_track = random.choice(level_tracks)
            if not self.past_artists.exist(random_track.artist) and\
                    not self.past_tracks.exist(random_track.track_uuid):
                break

        # If in the level which can not satisy both rules,pick one
        # randomly from all tracks
        if level_tracks:
            chosen_track = random.choice(level_tracks)
        else:
            chosen_track = random.choice(self.lib_list)
        self.past_tracks.append(chosen_track.track_uuid)
        self.past_artists.append(chosen_track.artist)
        chosen_track.type = "lib"
        return chosen_track
