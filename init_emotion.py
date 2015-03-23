from constants import redname
from models import userTrack, tagM
from utils import geventWorker, fredis
from controllers import emotion_contr


def init_emotion(username):
    '''
    start emotion tracks
    '''
    user_tracks = userTrack.choose_all_tracks(username)
    user_tracks = userTrack.choose_tracks_info(user_tracks)
    emotion_gevent = geventWorker.Worker(50, 'add_element')
    emotion_gevent.pack(user_tracks, emotion_contr.calculate_tags)
    lib_emotion_array = emotion_gevent.return_results()

    rec_tracks = userTrack.choose_rec_tracks(username)
    rec_tracks = userTrack.choose_tracks_info(rec_tracks)
    rec_gevent = geventWorker.Worker(50, 'add_element')
    rec_gevent.pack(rec_tracks, emotion_contr.calculate_tags)
    rec_emotion_array = rec_gevent.return_results()

    # emotion_contr.filter_no_tags(lib_emotion_array, rec_emotion_array)

    userTrack.add_tracks_emotion(lib_emotion_array + rec_emotion_array)


if __name__ == "__main__":
    ps = fredis.subscribe(redname.WAITING_EMO_USER)
    for message in ps.listen():
        if message['type'] == "message":
            username = message['data']
            init_emotion(username)
