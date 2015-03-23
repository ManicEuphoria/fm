from init_user import get_recommendation, init_emotion, refresh
from init_user import store_tracks_info
from utils import fredis
from constants import redname
from models import userM


if __name__ == '__main__':
    ps = fredis.subscribe(redname.WAITING_REC_USER)
    for message in ps.listen():
        if message['type'] == "message":
            username = message['data']
            get_recommendation(username)
            init_emotion(username)
            store_tracks_info(username)
            refresh(username, emotion_range=[100, 125])
            userM.add_to_all_finished(username)
