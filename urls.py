import tornado.web

from views import show


urls = [
    (r'/test', show.TestHandler),
    (r'/next', show.NextHandler),
]
