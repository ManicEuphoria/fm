from views.base import BaseHandler
from controllers.track_contr import get_next_song
from controllers import last_contr


class TestHandler(BaseHandler):
    def get(self):
        username = "patrickcai"
        tracks = get_next_song(username, number=2)
        self.render('test.html', track=tracks)


class NextHandler(BaseHandler):
    def get(self):
        username = "patrickcai"
        last_track = self.get_argument("last_track", None)
        this_track = self.get_argument("this_track", None)
        if last_track:
            last_contr.scrobble(username, last_track)
        if this_track:
            last_contr.update_playing(username, this_track)
        track = get_next_song(username)
        self.write({"url": track.url, "title": track.title,
                   'artist': track.artist})
