import os


API_KEY = "9196fd3c8cebc35c969bcd08cf69416d"
API_SECRET = "f0067afc3af73cb86a77bb50c3163784"


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MIN_TRACK_PLAYCOUNT = 3

TOP_RATIO = 40
RECENT_RATIO = 40
LOVED_RATIO = 20

MAX_PAST_ARTISTS = 15
MAX_PAST_TRACKS = 50

MIN_ARTIST_PLAYCOUNT = 200

LEVELS_ORDER = [4, 3, 2, 4, 3, 2, 1]

STORED_TRACKS_NUMBER = 20


SEARCH_URL = 'http://music.163.com/api/search/get'
API_HEADERS = {"Referer": "http://music.163.com"}
API_COOKIE = {"appver": '2.0.2'}
MP3_FILE_PREFIX = 'http://m1.music.126.net/'


NEIGHBOUR_RATE_RULES = {
    "start_value": 3,
    "end_value": 7,
}
NEIGHBOUR_OVERALL_RATE_RULES = {
    "start_value": 60,
    "end_value": 100,
}

WY_ARTIST_PREFIX = 'http://music.163.com/#/artist?id='
WY_ALBUM_PREFIX = "http://music.163.com/#/album?id="
WY_SONG_PREFIX = 'http://music.163.com/#/song?id='


def get_dfsid_url(song_id):
    url = r'http://music.163.com/api/song/detail/?id\
            =%s&ids=%s5B%s%s5D&csrf_token=Method=GET' % (
        song_id, '%', song_id, "%")
    return url
