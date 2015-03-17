import uuid

from constants.main import MIN_TRACK_PLAYCOUNT, NEIGHBOUR_OVERALL_RATE_RULES
from constants.main import LOVED_RATIO, NEIGHBOUR_RATE_RULES
from constants.main import MIN_ARTIST_PLAYCOUNT
from models import userTrack
from utils.rate import Rate, RateConvert
from utils.zeus import divide_level
from utils.log import visitlog


class TempTrack(object):
    def __init__(self, track_uuid, title, artist, ratio):
        self.track_uuid = track_uuid
        self.title = title
        self.artist = artist
        self.ratio = ratio
        self.track_id = None
        self.rate = None

    def __repr__(self):
        return "Track id %s,track title %s, rate %s, ratio %s artist %s" % (
            self.track_id, self.title, self.rate, self.ratio, self.artist)


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
    def __init__(self, tracks_list, ratio, track_list_type=None):
        self.tracks_list = tracks_list
        self.ratio = ratio
        self.track_list_type = track_list_type

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

    def sim_to_temp(self, all_top_tracks):
        '''
        Transform the similar tracks into the instance of class TempTrack
        and merge them
        '''
        temp_tracks = [TempTrack(str(uuid.uuid4())[0: 8],
                                 track.item.title, track.item.artist,
                                 self.ratio)
                       for track in self.tracks_list]
        have_tracks = {}
        for temp_track in temp_tracks:
            track_id = str(temp_track.title) + "||" + str(temp_track.artist)
            if track_id in have_tracks:
                have_tracks[track_id].frequency += 1
            else:
                temp_track.frequency = 1
                have_tracks[track_id] = temp_track
        final_tracks = sorted(have_tracks.values(), key=lambda x: x.frequency,
                              reverse=True)
        self.tracks_list = final_tracks
        final_tracks = self.filter_listened(all_top_tracks)[0: 2000]
        return final_tracks

    def neighbours_to_temp(self):
        '''
        the self.tracks_list type is [[Topitem(...user1), Topitem(...user1)],
                                      [Topitem(...user2), Topitem(...user2)]]
        1. Sort each neighours track list and turn tracks into instance of
            class TempTrack
        2. Merge one_neighbour_tracks and add rate
        3. Order the merged_neighbours_fav and re-rate the tracks
        '''
        all_users_tracks = []
        for one_user_tracks in self.tracks_list:
            one_user_tracks = sorted(one_user_tracks, key=lambda x: x.weight)
            # @todo(add the function for TempTrack(...))
            one_user_temp_tracks = [TempTrack(track.item.title,
                                              track.item.artist, self.ratio)
                                    for track in one_user_tracks
                                    if track.weight >= MIN_TRACK_PLAYCOUNT]
            rate_tracks = RateConvert(one_user_temp_tracks,
                                      **NEIGHBOUR_RATE_RULES)
            one_user_rated_tracks = rate_tracks.rate()
            all_users_tracks.extend(one_user_rated_tracks)
        neighbours_fav_tracks = self._merge_neighbours_tracks(all_users_tracks)
        self.tracks_list = neighbours_fav_tracks

    def rec_art_to_temp(self):
        '''
        the self.tracks_list type is [[Topitem(...user1), Topitem(...user1)],
                                      [Topitem(...user2), Topitem(...user2)]]
        1. transorm tracks into instance of TempTrack
        '''
        rec_art_tracks = [TempTrack(str(uuid.uuid4())[0: 8],
                                    track.item.title,
                                    track.item.artist, self.ratio)
                          for track in self.tracks_list
                          if track.weight >= MIN_ARTIST_PLAYCOUNT]
        return rec_art_tracks

    def _merge_neighbours_tracks(self, all_users_tracks):
        '''
        Merge one_neighbour_tracks and add rate
        '''
        neighbours_fav_tracks = {}
        for track in all_users_tracks:
            track_id = str(track.artist) + "||" + str(track.title)
            if track_id in neighbours_fav_tracks:
                neighbour_track = neighbours_fav_tracks[track_id]
                neighbour_track.rate += track.rate
            else:
                neighbours_fav_tracks[track_id] = track
        neighbours_fav_tracks = sorted(neighbours_fav_tracks.values(),
                                       key=lambda x: x.rate)
        for track in neighbours_fav_tracks:
            print(track)
        rate_tracks = RateConvert(neighbours_fav_tracks,
                                  **NEIGHBOUR_OVERALL_RATE_RULES)
        neighbours_fav_tracks = rate_tracks.rate()
        return neighbours_fav_tracks

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

    def filter_listened(self, top_tracks):
        '''
        Filter those track user have already listened
        Top_tracks is  a list contains the Topitem
        '''
        final_tracks = []
        top_tracks_ids = [str(track.item.title) + "||" + str(track.item.artist)
                          for track in top_tracks
                          if track.weight >= MIN_TRACK_PLAYCOUNT]
        for temp_track in self.tracks_list:
            track_id = str(temp_track.title) + "||" + str(temp_track.artist)
            if track_id not in top_tracks_ids:
                final_tracks.append(temp_track)
        return final_tracks


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


def rec_to_db(username, rec_tracks):
    '''
    Merge user's recommendation tracks and put them into database
    '''
    userTrack.add_rec_tracks(username, rec_tracks)
