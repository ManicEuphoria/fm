import json
import cPickle

from constants import main, redname
from utils import zeus
from utils.fredis import r_cli


class FixedLengthList(object):
    def __init__(self, length, username, limit_name):
        self.length = length
        self.key_name = "%slimit:%s" % (limit_name, username)

    def append(self, item):
        if r_cli.llen(self.key_name) >= self.length:
            r_cli.lpop(self.key_name)
        r_cli.rpush(self.key_name, item)

    def exist(self, item):
        '''
        Check whether the item is in the list
        '''
        items_in_list = r_cli.lrange(self.key_name, 0, -1)
        return True if item in items_in_list else False


class Emotion(object):
    def __init__(self, emotion=None):
        if emotion:
            self.emotion_range = emotion.emotion_range
            self.last_emotion = emotion.last_emotion
        else:
            self.emotion_range = zeus.choice(main.EMOTION_AREA)
            self.last_emotion = None
        self.extra_emotion_range = self._extra_emotion_range()

    def init_emotion_range(self):
        return [0, 100]

    def next_emotion_range(self, track_number):
        if track_number.track_number == 0:
            if track_number.continue_playing:
                next_playing_emotion_rules = {
                    0: [100, 200],
                    100: [0, 100],
                    200: [300, 400],
                    300: [200, 300],
                }
                close_emo_range_rule = {
                    0: [80, 100],
                    100: [100, 120],
                    200: [280, 300],
                    300: [300, 330],
                }
                start_value = self.emotion_range[0]
                self.emotion_range = next_playing_emotion_rules[start_value]
                start_value = self.emotion_range[0]
                self.close_emotion_range = close_emo_range_rule[start_value]
            else:
                next_emotion_rules = {
                    0: [200, 300],
                    100: [300, 400],
                    200: [100, 200],
                    300: [0, 100],
                }
                start_value = self.emotion_range[0]
                self.emotion_range = next_emotion_rules[start_value]
        self.extra_emotion_range = self._extra_emotion_range()

    def _extra_emotion_range(self):
        '''
        When pick a list of tracks, emotion range can be larger
        than the original length 100
        '''
        extra_value = 25
        emotion_range = [self.emotion_range[0] - extra_value,
                         self.emotion_range[1] + extra_value]
        return emotion_range

    def change_emotion(self, last_emotion):
        '''
        Next status of emotion to change the last emotion
        '''
        self.last_emotion = last_emotion

    def __repr__(self):
        return "The emotion range %s\nThe last emotion value %s" % (
            self.emotion_range, self.last_emotion)


class Tag(object):
    def __init__(self, last_tag=None, last_tag_value=None):
        self.last_tag = last_tag
        self.last_tag_value = last_tag_value

    def next(self, last_track, past_tags, do_skip):
        '''
        According to the tag history to choose the tag of the next track
        '''
        tags = last_track.tags
        if do_skip:
            self.last_tag = None
            self.last_tag_value = None
            return
        for last_tag, last_tag_value in tags.iteritems():
            if not past_tags.exist(last_tag) and last_tag_value >= 10:
                self.last_tag = last_tag
                self.last_tag_value = last_tag_value
                past_tags.append(last_tag)
                break
        else:
            self.last_tag = None
            self.last_tag_value = None

    def __repr__(self):
        return "The last tag is %s\nThe last tag value is %s" % (
            self.last_tag, self.last_tag_value)


class TrackNumber(object):
    def __init__(self, n=None):
        self.track_length = 5
        self.track_number = n.track_number if n else 0
        self.continue_playing = n.continue_playing if n else False
        self.has_source = n.has_source if n else True

    def restart(self):
        self.track_number = 0
        self.continue_playing = False

    def next(self, do_skip):
        self.continue_playing = True
        self.has_source = True
        if self.track_number + 1 == self.track_length or do_skip:
            self.track_number = 0
            if do_skip:
                self.continue_playing = False
        else:
            if self.track_number == 1 and do_skip:
                self.track_number = 3
            else:
                self.track_number += 1

    def show(self):
        '''
        Show the track_number
        '''
        return self.track_number

    def __repr__(self):
        return "The track number is %s\nThe continue playing is %s\nss%s" % (
            self.track_number, self.continue_playing, self.has_source)


class RedisStatus(object):
    '''
    Some of the attr value are stored in the redis
    REQUIRED:
        1. self.redis_name to indicate the redis name
        2. self.username to indicate whose redis
        3. self.status_list to point out the statuses should stored in
           the redis
    '''
    def __init__(self):
        pass

    def _get_status(self):
        status_values = r_cli.hmget('%s%s' % (
            self.username, self.redis_name), self.status_list)
        for status, status_value in zip(self.status_list, status_values):
            value = cPickle.loads(status_value) if status_value else None
            setattr(self, status, value)

    def _set_status(self):
        redis_mapping = {}
        for attr in self.status_list:
            value = getattr(self, attr)
            redis_mapping[attr] = cPickle.dumps(value)

        r_cli.hmset('%s%s' % (self.username, self.redis_name),
                    redis_mapping)


class UserStatus(RedisStatus):
    def __init__(self, username):
        super(RedisStatus, self).__init__()
        self.username = username
        self.status_list = ['radio_type', 'track_number', "last_track",
                            "lib_ratio", "skip_times", 'tag', "emotion",
                            ]
        self.redis_name = redname.PERSONAL_STATUS
        self.past_artists = FixedLengthList(
            main.MAX_PAST_EMOTION_ARTISTS, username, 'artists')
        self.past_tracks = FixedLengthList(
            main.MAX_PAST_EMOTION_TRACKS, username, 'tracks')
        self.past_tags = FixedLengthList(
            main.MAX_PAST_TAGS, username, 'tags')
        self._get_status()

    def init_status(self):
        self.radio_type = main.INIT_RADIO_TYPE
        self.track_number = TrackNumber()
        self.last_track = None
        self.lib_ratio = main.LIB_RATIO
        self.skip_times = 0
        self.tag = Tag()
        self.emotion = Emotion()
        self._set_status()
        self._show_status()

    def next_status(self, last_track):
        '''
        1. Judge whether skip the track and restart track
        2. Update other status
        '''
        do_skip = self.do_skip(last_track)
        self.tag = Tag()
        self.tag.next(self.last_track, self.past_tags, do_skip)
        self.track_number = TrackNumber(self.track_number)
        self.track_number.next(do_skip)
        self.emotion = Emotion(self.emotion)
        self.emotion.next_emotion_range(self.track_number)
        self._set_status()
        self._show_status()

    def post_update_status(self, next_track):
        '''
        After pick the track update the status
        '''
        self.past_artists.append(next_track.artist)
        self.past_tracks.append(next_track.title)
        self.last_track = next_track
        self.emotion = Emotion(self.emotion)
        self.emotion.change_emotion(next_track.emotion_value)
        self._set_status()

    def do_skip(self, last_track):
        '''
        update user's status and
        Return Bool whether the playlist should be skipped
        '''
        do_skip = False
        if not last_track:
            skip_times_rules = lambda x: False if x == 0 else True
            skip_rules = {
                0: True,
                1: False,
                2: False,
                3: skip_times_rules(self.skip_times),
                4: skip_times_rules(self.skip_times)
            }
            do_skip = skip_rules[self.track_number.track_number]
        if do_skip:
            self.skip_times = 0
        elif not last_track:
            self.skip_times += 1
        self._set_status()
        return do_skip

    def is_first_track(self):
        return True if self.track_number.track_number == 0 else False

    def _show_status(self):
        '''
        Show all the status
        '''
        print("The track number is %s" % (self.track_number.track_number))
        print("The last chosen tag is %s, the tag value is %s" % (
            self.tag.last_tag, self.tag.last_tag_value))
        print("The emotion range is %s" % (self.emotion.emotion_range))


if __name__ == "__main__":
    s = UserStatus("Patrickcai")
    s.init_status()
