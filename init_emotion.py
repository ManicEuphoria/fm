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


def refresh_no_emotion_tracks():
    '''
    Retry to get the emotion value of the tracks withou the emotion value
    in the db
    '''
    no_emotion_tracks = userTrack.choose_no_emotion_tracks()
    emo_gevent = geventWorker.Worker(65, 'add_element')
    emo_gevent.pack(no_emotion_tracks, emotion_contr.calculate_tags)
    emo_array = emo_gevent.return_results()

    userTrack.add_tracks_emotion(emo_array)


if __name__ == "__main__":
    refresh_no_emotion_tracks()
    exit()
    ps = fredis.subscribe(redname.WAITING_EMO_USER)
    for message in ps.listen():
        if message['type'] == "message":
            username = message['data']
            init_emotion(username)
