import uuid

from constants.main import MIN_TRACK_PLAYCOUNT
from constants.main import LOVED_RATIO
from models.track import add_tracks
from models import userTrack
from utils.rate import Rate
from utils.zeus import divide_level


class TempTrack(object):
    def __init__(self, title, artist, ratio):
        self.title = title
        self.artist = artist
        self.ratio = ratio
        self.track_id = None
        self.rate = None

    def __repr__(self):
        return "Track id %s,track title %s, rate %s, ratio %s" % (
            self.track_id, self.title, self.rate, self.ratio)


class RateTrack(object):
    def __init__(self, track_uuid, title, artist, is_star, final_rate):
        self.track_uuid = track_uuid
        self.title = title
        self.artist = artist
        self.is_star = is_star
        self.final_rate = final_rate
        self.level = None

    def __repr__(self):
        return "track title %s, is_star %s, final_rate %s level %s" % (
            self.title, self.is_star, self.final_rate, self.level)


class TrackList(object):
    def __init__(self, tracks_list, ratio):
        self.tracks_list = tracks_list
        self.ratio = ratio

    def top_to_temp(self):
        '''
        Sort the tracks, filter tracks
        turn tracks into class instance TempTrack
        '''
        top_tracks = sorted(self.tracks_list, key=lambda x: x.weight)
        top_tracks = [TempTrack(track.item.title, track.item.artist,
                                self.ratio)
                      for track in top_tracks
                      if track.weight >= MIN_TRACK_PLAYCOUNT]
        top_tracks = self._rate_track(top_tracks)
        return top_tracks

    def _rate_track(self, top_tracks):
        '''
        Rate all tracks
        Return the rated tracks
        '''
        track_number = len(top_tracks)
        track_rate = Rate(track_number)
        for num, top_track in enumerate(top_tracks):
            rate_value = track_rate.add_rate(num)
            top_track.rate = rate_value
        return top_tracks

    def loved_to_temp(self):
        '''
        turn tracks into class instance TempTrack
        '''
        loved_tracks = [TempTrack(loved_track.track.title,
                                  loved_track.track.artist, self.ratio)
                        for loved_track in self.tracks_list]
        for loved_track in loved_tracks:
            loved_track.rate = self.ratio
        return loved_tracks


def merge(*args):
    '''
    1.Merge all the temp tracks list into one list
    2.Add the rate value
    3.Divide all track into different levels
    '''
    final_tracks_list = []
    for arg in args:
        final_tracks_list.extend(arg)

    rate_tracks_list = {}
    for temp_track in final_tracks_list:
        temp_title = temp_track.title
        temp_artist = temp_track.artist
        track_id = str(temp_title) + "||" + str(temp_artist)
        if track_id in rate_tracks_list:
            rate_value = temp_track.rate * temp_track.ratio
            rate_tracks_list[track_id].final_rate += rate_value
        else:
            is_star = 1 if temp_track.ratio == LOVED_RATIO else 0
            track_uuid = str(uuid.uuid4())[0: 8]
            final_rate = temp_track.rate * temp_track.ratio
            rate_track = RateTrack(track_uuid, temp_title, temp_artist,
                                   is_star, final_rate)
            rate_tracks_list[track_id] = rate_track

    rate_tracks_list = rate_tracks_list.values()
    rate_tracks_list = sorted(rate_tracks_list, key=lambda x: x.final_rate)
    for num, rate_track in enumerate(rate_tracks_list):
        rate_track.level = divide_level(num, len(rate_tracks_list))
    return rate_tracks_list


def add_track_level(username, final_track_list):
    userTrack.add_tracks(username, final_track_list)
