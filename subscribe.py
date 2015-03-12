from constants import redname
from utils import fredis
from refresh import refresh_emotion

if __name__ == "__main__":
    ps = fredis.r_cli.pubsub()
    ps.subscribe(redname.EMOTION_REFRESH)
    for message in ps.listen():
        if message['type'] == 'message':
            msg = message['data'].split('||')
            username = msg[0]
            emotion = msg[1]
            refresh_emotion(username, emotion)
