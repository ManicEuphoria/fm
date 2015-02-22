import UserList
import random
from constants.main import MAX_PAST_ARTISTS, LEVELS_ORDER


class ArtistList(UserList.UserList):
    def __init__(self, length):
        super(ArtistList, self).__init__()
        self.length = length

    def append(self, artist):
        if len(self) >= self.length:
            super(ArtistList, self).pop(0)
        super(ArtistList, self).append(artist)


class Picker(object):
    def __init__(self, tracks_list):
        self.tracks_list = tracks_list
        self.past_artists = ArtistList(MAX_PAST_ARTISTS)
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
                        track.artist not in self.past_artists]
        # If in the level which can not satisy both rules,pick one
        # randomly from all tracks
        if level_tracks:
            chosen_track = random.choice(level_tracks)
        else:
            chosen_track = random.choice(self.tracks_list)
        self.past_artists.append(chosen_track.artist)
        return chosen_track
