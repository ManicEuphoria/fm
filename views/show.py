from views.base import BaseHandler
from controllers.track_contr import get_next_song


class TestHandler(BaseHandler):
    def get(self):
        username = "patrickcai"
        track = get_next_song(username)
        print(track.url)
        print(track.title)
        self.render('test.html', track=track)


class NextHandler(BaseHandler):
    def get(self):
        username = "patrickcai"
        track = get_next_song(username)
        self.write({"url": track.url, "title": track.title,
                   'artist': track.artist})
