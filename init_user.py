import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time

from controllers import last_contr, track_contr
from controllers import trackList_contr, user_contr
from models import userM
from constants.main import TOP_RATIO, RECENT_RATIO, LOVED_RATIO
from utils.geventWorker import Worker
from utils.log import visitlog
from refresh import refresh

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


def get_top_tracks(username):
    playcount = last_contr.get_playcount(username)
    all_page_number = playcount / 2000
    # all_page_number = 5
    all_track_tasks = xrange(1, all_page_number + 1)
    all_track_gevent = Worker(50)
    all_track_boss = all_track_gevent.generate_boss(all_track_tasks)
    all_track_workers = all_track_gevent.generate_workers(
        last_contr.get_all_top_tracks, username)
    all_track_gevent.joinall(all_track_boss, all_track_workers)
    tracks_list = all_track_gevent.return_results()
    return tracks_list


def get_rec_artists_tracks(rec_artists):
    '''
    From recommendation artists, we can get the artists' top tracks
    '''
    rec_artists_gevent = Worker(50)
    rec_artists_tracks = rec_artists_gevent.pack(
        rec_artists, last_contr.get_artist_top_tracks)
    rec_art_tracks_list = trackList_contr.TrackList(
        rec_artists_tracks, 40, track_list_type="rec_artists")
    final_tracks = rec_art_tracks_list.rec_art_to_temp()
    return final_tracks


def get_rec_similar_tracks(user_top_tracks, all_top_tracks):
    '''
    Get the track's similar tracks
    '''
    similar_tracks = Worker(30)
    similar_tracks = similar_tracks.pack(
        user_top_tracks, last_contr.get_similar_tracks)
    similar_tracks = trackList_contr.TrackList(
        similar_tracks, 40)
    final_tracks = similar_tracks.sim_to_temp(all_top_tracks)
    return final_tracks

###########################################################################


def get_own_library(username):
    '''
    1. Get all top tracks in recent one year(recent, or loved)
    2. Transform the tracks list into the instance of class TrackList
        and transform each track into the instance of class TempTrack
    3. Merge all lists into one list, and rate tracks
    4. Add user track into database
    '''
    all_temp_tracks = _gevent_task(
        50, ALL_PAGE_NUMBER, last_contr.get_top_tracks, TOP_RATIO)
    recent_temp_tracks = _gevent_task(
        50, RECENT_PAGE_NUMBER, last_contr.get_recent_tracks, RECENT_RATIO)
    loved_temp_tracks = _gevent_task(
        50, LOVED_PAGE_NUMBER, last_contr.get_loved_tracks, LOVED_RATIO)

    final_tracks_list = trackList_contr.merge(
        all_temp_tracks, recent_temp_tracks, loved_temp_tracks)

    trackList_contr.add_track_level(username, final_tracks_list)


def get_recommendation(username):
    all_top_tracks = get_top_tracks(username)
    rec_artists = last_contr.get_rec_artists(username)
    rec_artists_tracks = get_rec_artists_tracks(rec_artists)

    user_top_tracks = track_contr.get_user_top_tracks(username)
    rec_similar_tracks = get_rec_similar_tracks(user_top_tracks,
                                                all_top_tracks)
    rec_tracks = rec_artists_tracks + rec_similar_tracks
    trackList_contr.rec_to_db(username, rec_tracks)


def init(username):
    get_own_library(username)
    refresh(username, refresh_type="init")
    get_recommendation(username)
    refresh(username)


if __name__ == '__main__':
    while 1:
        username = user_contr.get_waiting_user()
        if username:
            last_user = last_contr.get_user(username)
            a = time.time()
            init(username)
            userM.del_waiting_user(username)
            print(time.time() - a)
        else:
            print("wait 5")
            time.sleep(5)
