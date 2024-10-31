from tornado.web import Application
import tornado.ioloop
from typing import List, Tuple, Type


def make_app(routes: List[Tuple[str, Type, dict]]) -> Application:
    return Application(routes)


def run_socket(port: int, routes: List[Tuple[str, Type, dict]]) -> None:
    app = make_app(routes)
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
