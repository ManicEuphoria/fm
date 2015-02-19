import tornado.web

from views import show


urls = [
    (r'/', show.TestHandler),
]
