import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from controllers.track_contr import choose_tracks, filter_no_tracks
from controllers.info import fetch_tracks_urls
# from controllers.last_contr import get_extra_info
from controllers.track_contr import store_urls

if __name__ == '__main__':
    '''
    1. Choose those tracks from database
    2. Get extra info about those songs
    2. Get song id  from wangyi
    3. Put them in redis
    '''
    username = "patrickcai"
    chosen_tracks = choose_tracks(username)
    # chosen_tracks = get_extra_info(chosen_tracks)
    fetch_tracks_urls(chosen_tracks)
    chosen_tracks = filter_no_tracks(chosen_tracks)
    store_urls(username, chosen_tracks)
