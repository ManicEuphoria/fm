from views.base import BaseHandler


class TestHandler(BaseHandler):
    def get(self):
        self.write("Yes")
