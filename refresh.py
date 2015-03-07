import sys
import time
reload(sys)
sys.setdefaultencoding("utf-8")

from models import userTrack, userM
from controllers import user_contr
from controllers.track_contr import choose_tracks, filter_no_tracks
from controllers.info import fetch_tracks_urls
# from controllers.last_contr import get_extra_info
from controllers.track_contr import store_urls, choose_init_tracks


def refresh(username, refresh_type='normal'):
    '''
    1. Choose those tracks from database
    2. Get extra info about those songs
    2. Get song id  from wangyi
    3. Put them in redis
    '''
    if refresh_type == "normal":
        chosen_tracks = choose_tracks(username)
    else:
        chosen_tracks = choose_init_tracks(username)
        # chosen_tracks = get_extra_info(chosen_tracks)
    fetch_tracks_urls(chosen_tracks)
    chosen_tracks = filter_no_tracks(chosen_tracks)
    store_urls(username, chosen_tracks)


def check_and_refresh(username):
    '''
    Check whether user's remaining tracks and refresh them
    '''
    remain_number = userTrack.remain_tracks(username)
    # @todo(If the user is refreshing then stop refreshing)
    print("remaing number is %s" % (remain_number))
    if remain_number <= 20:
        refresh(username)


if __name__ == '__main__':
    while 1:
        usernames = userM.get_all_users()
        usernames = [user.username for user in usernames
                     if not userM.is_in_waiting_user(user.username)]
        print(usernames)
        users_tracks = []
        for username in usernames:
            remain_number = userTrack.remain_tracks(username)
            print(remain_number)
            if remain_number <= 20:
                users_tracks.append([username, remain_number])
        users_in_update = sorted(users_tracks, key=lambda x: x[1])
        users_in_update = [user[0] for user in users_in_update]
        print(users_in_update)
        for username in users_in_update:
            refresh(username)

        a = 1
        a += 1
        del a
        print('wait 30')
        time.sleep(30)
