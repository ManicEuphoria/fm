import collections
from constants import main

from utils.zeus import AttrGet


class NextTrack(AttrGet):
    def __init__(self, track, lib_type, lib_tracks):
        self.attr_list = ["track_uuid", "title", "artist", "mp3_url",
                          "album_url", "album_id", "artist_id",
                          "duration", "song_id", "emotion_value"]
        self._get_attr(track)
        self.tags = collections.OrderedDict()
        for i in xrange(1, 5):
            tag = getattr(track, 'tag%s' % (i))
            tag_value = getattr(track, "tag_value%s" % (i))
            if not tag:
                break
            self.tags[tag] = tag_value
        for lib_track in lib_tracks:
            if lib_track.track_uuid == track.track_uuid:
                self.lib_type = lib_type
                if lib_type == "lib":
                    self.level = lib_track.level
                    self.is_star = lib_track.is_star
                elif lib_type == "rec":
                    self.source_type = lib_track.source_type
                    self.source = lib_track.source
                    self.is_star = 0
                break
        self._extra_info()

    def __repr__(self):
        return "The title is %s\nThe artist is %s\n\
                The emotion value is %s\nThe tags are %s" % (
            self.title, self.artist, self.emotion_value, self.tags)

    def _extra_info(self):
        '''
        Add the prefix into the info about the track
        like the mp3 url
        '''
        self.mp3_url = main.MP3_FILE_PREFIX + self.mp3_url + '.mp3'
        self.artist_id = main.WY_ARTIST_PREFIX + self.artist_id
        self.album_id = main.WY_ALBUM_PREFIX + self.album_id
        self.song_id = main.WY_SONG_PREFIX + self.song_id
