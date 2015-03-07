import tornado.web

from views import show


urls = [
    (r'/', show.MainHandler),
    (r'/test', show.TestHandler),
    (r'/next', show.NextHandler),
    (r'/love', show.LoveHandler),
    (r'/unlove', show.UnloveHandler),
    (r'/loading', show.LoadHandler),
    (r'/status', show.StatusHandler),
    (r'/check', show.CheckHandler),
]
