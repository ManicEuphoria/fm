import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time

from controllers import last_contr, track_contr
from controllers import trackList_contr
from constants.main import TOP_RATIO, RECENT_RATIO, LOVED_RATIO
from utils.geventWorker import Worker
from utils.log import visitlog

ALL_PAGE_NUMBER = 30
RECENT_PAGE_NUMBER = 10
LOVED_PAGE_NUMBER = 1


def _gevent_task(worker_number, page_number, func, ratio):
    '''
    1. Get all top tracks in recent one year(recent, or loved)
    2. Transform the tracks list into the instance of class TrackList
        and transform each track into the instance of class TempTrack
    '''
    gevent_worker = Worker(worker_number)
    tasks = xrange(1, page_number + 1)
    boss = gevent_worker.generate_boss(tasks)
    workers = gevent_worker.generate_workers(
        func, last_user)
    gevent_worker.joinall(boss, workers)

    tracks_list = gevent_worker.return_results()
    new_tracks_list = trackList_contr.TrackList(tracks_list, ratio)
    if ratio == LOVED_RATIO:
        temp_tracks = new_tracks_list.loved_to_temp()
    else:
        temp_tracks = new_tracks_list.top_to_temp()
    return temp_tracks


def get_own_library(username):
    '''
    1. Get all top tracks in recent one year(recent, or loved)
    2. Transform the tracks list into the instance of class TrackList
        and transform each track into the instance of class TempTrack
    3. Merge all lists into one list, and rate tracks
    4. Add user track into database
    '''
    all_temp_tracks = _gevent_task(
        30, ALL_PAGE_NUMBER, last_contr.get_top_tracks, TOP_RATIO)
    recent_temp_tracks = _gevent_task(
        20, RECENT_PAGE_NUMBER, last_contr.get_recent_tracks, RECENT_RATIO)
    loved_temp_tracks = _gevent_task(
        10, LOVED_PAGE_NUMBER, last_contr.get_loved_tracks, LOVED_RATIO)

    final_tracks_list = trackList_contr.merge(
        all_temp_tracks, recent_temp_tracks, loved_temp_tracks)

    track_contr.add_track_level(username, final_tracks_list)


if __name__ == '__main__':
    start_time = time.time()
    username = "patrickcai"
    last_user = last_contr.get_user(username)
    get_own_library(username)
    print(time.time() - start_time)
