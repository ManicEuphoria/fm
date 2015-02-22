import random
from constants.main import MAX_PAST_ARTISTS, LEVELS_ORDER, MAX_PAST_TRACKS
from utils import fredis


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
    def __init__(self, tracks_list, username):
        self.tracks_list = tracks_list
        self.past_artists = FixedLengthList(MAX_PAST_ARTISTS, username,
                                            "artists")
        self.past_tracks = FixedLengthList(MAX_PAST_TRACKS, username,
                                           "tracks")
        self.pick_pos = 0

    def _next_pos(self):
        '''
        Next position in the levels orders
        '''
        if self.pick_pos == (len(LEVELS_ORDER) - 1):
            self.pick_pos = 0
        else:
            self.pick_pos += 1

    def next_lib(self):
        '''
        Choose next track from the user's own library
        '''
        level = LEVELS_ORDER[self.pick_pos]
        self._next_pos()
        level_tracks = [track for track in self.tracks_list
                        if track.level == level and
                        not self.past_artists.exist(track.artist) and
                        not self.past_tracks.exist(track.track_uuid)]
        # If in the level which can not satisy both rules,pick one
        # randomly from all tracks
        if level_tracks:
            chosen_track = random.choice(level_tracks)
        else:
            chosen_track = random.choice(self.tracks_list)
        self.past_tracks.append(chosen_track.track_uuid)
        self.past_artists.append(chosen_track.artist)
        return chosen_track
