from models import userTrack, tagM
from utils import geventWorker
from controllers import emotion_contr


def init_emotion(username):
    user_tracks = userTrack.choose_all_tracks(username)[0: 20]
    emotion_gevent = geventWorker.Worker(35, 'add_element')
    emotion_gevent.pack(user_tracks, emotion_contr.calculate_tags)
    lib_emotion_array = emotion_gevent.return_results()

    rec_tracks = userTrack.choose_rec_tracks(username)[0: 20]
    rec_gevent = geventWorker.Worker(35, 'add_element')
    rec_gevent.pack(rec_tracks, emotion_contr.calculate_tags)
    rec_emotion_array = rec_gevent.return_results()

    emotion_contr.filter_no_tags(lib_emotion_array, rec_emotion_array)

    tagM.store_emotion(username, lib_emotion_array, 'lib')
    tagM.store_emotion(username, rec_emotion_array, 'rec')


if __name__ == "__main__":
    init_emotion()
