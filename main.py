import tornado.ioloop
import tornado.web
import tornado.websocket

from games.arkanoid import ArkanoidWebSocketHandler


def make_app():
    return tornado.web.Application([
        (r"/ws/arkanoid/", ArkanoidWebSocketHandler),
    ])


def run():
    app = make_app()
    app.listen(8001)
    print("Started")
    tornado.ioloop.IOLoop.current().start()


run()
