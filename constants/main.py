import os


API_KEY = "2e6e98ec329aa9c86bb8a541fc09bd29"
API_SECRET = "c86c14938f3344707b0a56a0a1370e69"


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MIN_TRACK_PLAYCOUNT = 4

TOP_RATIO = 40
RECENT_RATIO = 40
LOVED_RATIO = 20

MAX_PAST_ARTISTS = 6

LEVELS_ORDER = [4, 3, 2, 1]

STORED_TRACKS_NUMBER = 50


SEARCH_URL = 'http://music.163.com/api/search/get'
API_HEADERS = {"Referer": "http://music.163.com"}
API_COOKIE = {"appver": '2.0.2'}
MP3_FILE_PREFIX = 'http://m1.music.126.net/'


def get_dfsid_url(song_id):
    url = r'http://music.163.com/api/song/detail/?id\
            =%s&ids=%s5B%s%s5D&csrf_token=Method=GET' % (
        song_id, '%', song_id, "%")
    return url
