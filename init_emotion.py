from models import userTrack, tagM
from utils import geventWorker
from controllers import emotion_contr


def init_emotion():
    username = "Patrickcai"
    user_tracks = userTrack.choose_all_tracks(username)
    emotion_gevent = geventWorker.Worker(35, 'add_element')
    emotion_gevent.pack(user_tracks, emotion_contr.calculate_tags)
    emotion_array = emotion_gevent.return_results()
    tagM.store_emotion(username, emotion_array, 'lib')

    rec_tracks = userTrack.choose_rec_tracks(username)
    rec_gevent = geventWorker.Worker(35, 'add_element')
    rec_gevent.pack(rec_tracks, emotion_contr.calculate_tags)
    emotion_array = rec_gevent.return_results()
    tagM.store_emotion(username, emotion_array, 'rec')


if __name__ == "__main__":
    init_emotion()
