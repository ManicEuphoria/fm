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


def get_top_tracks(username):
    playcount = last_contr.get_playcount(username)
    all_page_number = playcount / 2000
    # all_page_number = 5
    all_track_tasks = xrange(1, all_page_number + 1)
    all_track_gevent = Worker(30)
    all_track_boss = all_track_gevent.generate_boss(all_track_tasks)
    all_track_workers = all_track_gevent.generate_workers(
        last_contr.get_all_top_tracks, username)
    all_track_gevent.joinall(all_track_boss, all_track_workers)
    tracks_list = all_track_gevent.return_results()
    return tracks_list


def get_neighbours_fav(neighbours, all_top_tracks):
    '''
    1. Get neighour favourtie track lists
    2. Transform the tracks list into the instance of class Tracklist
        and transform each track into the instance of class Temptrack
    3. Rate each track
    4. Filter those tracks which user have already listened
    '''
    neighbours_gevent = Worker(30, results_type="add_element")
    user_pages = []
    for neighbour in neighbours:
        for page_number in xrange(1, 3):
            user_page = [neighbour, page_number]
            user_pages.append(user_page)

    neighbours_top_tracks = neighbours_gevent.pack(
        user_pages, last_contr.get_neighbours_fav)

    # @todo(Add the ratio)
    neighbours_tracks_list = trackList_contr.TrackList(
        neighbours_top_tracks, 40, track_list_type="neighbour")
    neighbours_tracks_list.neighbours_to_temp()
    final_tracks = neighbours_tracks_list.filter_listened(all_top_tracks)
    return final_tracks


def get_recommendation(username):
    all_top_tracks = get_top_tracks(username)
    neighbours = last_contr.get_neighbours(username)
    neighbours_fav_tracks = get_neighbours_fav(neighbours,
                                               all_top_tracks)


if __name__ == '__main__':
    start_time = time.time()
    username = "patrickcai"
    last_user = last_contr.get_user(username)
    # get_own_library(username)
    get_recommendation(username)
    print(time.time() - start_time)
