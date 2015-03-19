import sys
import json
import time
reload(sys)
sys.setdefaultencoding("utf-8")

from models import userTrack, userM, tagM
from controllers import user_contr
from controllers import track_contr
from constants import main, redname
from controllers.track_contr import choose_tracks, filter_no_tracks
from controllers.info import fetch_tracks_urls
from controllers.track_contr import store_urls, choose_init_tracks
from utils import fredis


def refresh(username, lib_ratio=main.LIB_RATIO, refresh_type='normal',
            emotion_range=None):
    '''
    1. Choose those tracks from database
    2. Get extra info about those songs
    2. Get song id  from wangyi
    3. Put them in redis
    '''
    next_playlist_track = None
    if refresh_type == "normal":
        chosen_tracks, next_playlist_track = choose_tracks(
            username, lib_ratio, emotion_range)
    else:
        chosen_tracks = choose_init_tracks(username)
    fetch_tracks_urls(chosen_tracks)
    chosen_tracks = filter_no_tracks(chosen_tracks)
    store_urls(username, chosen_tracks,
               next_playlist_track=next_playlist_track)


def check_and_refresh(username):
    '''
    Check whether user's remaining tracks and refresh them
    '''
    remain_number = userTrack.remain_tracks(username)
    # @todo(If the user is refreshing then stop refreshing)
    print("remaing number is %s" % (remain_number))
    if remain_number <= 20:
        refresh(username)


def refresh_emotion(username, emotion):
    '''
    Refresh user's track in certain emotion
    '''
    emotion_tracks = tagM.get_emotion_tracks(username, emotion)
    chosen_tracks = track_contr.choose_emotion_tracks(username, emotion_tracks,
                                                      emotion)
    fetch_tracks_urls(chosen_tracks)
    chosen_tracks = filter_no_tracks(chosen_tracks)
    store_urls(username, chosen_tracks, erase='True', radio_type="emotion")


if __name__ == '__main__':
    ps = fredis.r_cli.pubsub()
    ps.subscribe(redname.PLAYLIST_REFRESH)
    for message in ps.listen():
        if message['type'] == "message":
            refresh_msg = json.loads(message['data'])
            username = refresh_msg["username"]
            lib_ratio = refresh_msg["lib_ratio"]
            emotion_range = refresh_msg["emotion_range"]
            refresh(username, lib_ratio=lib_ratio, refresh_type="normal",
                    emotion_range=emotion_range)
