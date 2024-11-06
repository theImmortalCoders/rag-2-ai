import json

from tornado.web import RequestHandler


class RoutesHandler(RequestHandler):
    def initialize(self, routes):
        self.routes = routes

    def get(self):
        routes_info = [{"path": route[0], "name": route[1].__name__} for route in self.routes]
        self.write(json.dumps(routes_info))
