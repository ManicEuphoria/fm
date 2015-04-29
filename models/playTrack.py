import random

from models import user_status
from models import userTrack
from models.nextTrack import NextTrack
from constants import track_rule
from constants import redname
from utils import zeus
from constants import main


class TrackList(object):
    def __init__(self, username):
        self.username = username
        self.user_status = user_status.UserStatus(username)

    def next_track(self, last_track=None, is_restart=False):
        '''
        1. next status
        2. get the next track
        3. post update the status
        '''
        if is_restart:
            self.user_status.init_status()
        else:
            self.user_status.next_status(last_track)

        self._filter_tracks()
        next_track = self._order_tracks()
        self.user_status.post_update_status(next_track)
        print(next_track)
        return next_track

    def _filter_tracks(self):
        '''
        Get the tracks from the db and make it
        into the instance of the class NextTrack
        '''
        if self.user_status.last_track:
            last_title = self.user_status.last_track.title
        else:
            last_title = None
        username = self.user_status.username
        while 1:
            emo_range, tag, lib = track_rule.track_rule(
                "filter", self.user_status)
            emo_range = emo_range(self.user_status) if emo_range else None
            tag = tag(self.user_status) if tag else None
            if lib == "lib":
                self.lib_tracks = userTrack.choose_all_tracks(username)
            elif lib == "rec":
                self.rec_tracks = userTrack.choose_rec_tracks(username)
            lib_uuids = [track.track_uuid
                         for track in getattr(self, "%s_tracks" % (lib))]
            if not emo_range and not tag:
                self.sample_tracks = userTrack.get_source_rec(
                    last_title, username)
                if not self.sample_tracks:
                    print("No similar rec")
                    self.user_status.track_number.has_source = False
                else:
                    break
            else:
                self.sample_tracks = userTrack.get_user_tracks_detail(
                    emo_range, tag, lib_uuids)

                if self.sample_tracks:
                    break
                else:
                    # @todo
                    pass
        self.chosen_tracks = getattr(self, '%s_tracks' % (lib))
        self.lib = lib
        random.shuffle(self.sample_tracks)

    def _order_tracks(self):
        '''
        Order these tracks based on the last emotion, last_tag and track number
        '''
        order, limit = track_rule.track_rule("order", self.user_status)

        if order == "level":
            # No necessary to compare this emotion value and last
            # choose the tracks with higher level
            for wait_track in self.sample_tracks:
                wait_track = NextTrack(wait_track, self.lib,
                                       self.chosen_tracks)
                if not self._is_artist_track_limit(wait_track)\
                        and wait_track.level in [3, 4]:
                    return wait_track
        if order == "order":
            last_emotion_value = self.user_status.emotion.last_emotion
            last_tag = self.user_status.tag.last_tag
            last_tag_value = self.user_status.tag.last_tag_value
            self._order_emo_tag(last_emotion_value, last_tag_value, last_tag)
            for wait_track in self.sample_tracks:
                wait_track = NextTrack(wait_track, self.lib,
                                       self.chosen_tracks)
                if not self._is_artist_track_limit(wait_track):
                    return wait_track
            # @(todo) not elegant
            else:
                wait_track = zeus.choice(self.sample_tracks)
                wait_track = NextTrack(wait_track, self.lib,
                                       self.chosen_tracks)
                return wait_track

    def _is_artist_track_limit(self, wait_track):
        artist = wait_track.artist
        track_uuid = wait_track.track_uuid
        if self.user_status.past_artists.exist(artist) or\
                self.user_status.past_tracks.exist(track_uuid):
            return True
        else:
            return False

    def _order_emo_tag(self, last_emotion_value, last_tag_value, last_tag):
        for wait_track in self.sample_tracks:
            this_emotion_value = wait_track.emotion_value
            for i in xrange(1, 5):
                tag = getattr(wait_track, "tag%s" % (i))
                if tag == last_tag:
                    this_tag_value = getattr(wait_track, "tag_value%s" % (i))
                    break
            else:
                this_tag_value = 0
            eq = lambda x, y: x if x else y
            last_emotion_value = eq(last_emotion_value, this_emotion_value)
            if not this_tag_value:
                this_tag_value = 0
            last_tag_value = eq(last_tag_value, this_tag_value)
            diff_value = abs(this_emotion_value - last_emotion_value) +\
                abs(this_tag_value - last_tag_value)
            wait_track.diff_value = diff_value
        self.sample_tracks = sorted(self.sample_tracks,
                                    key=lambda x: x.diff_value)
