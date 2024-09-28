import threading

import tornado.ioloop
import tornado.web
import tornado.websocket

from games.pong.pong import PongGesturesHandler, PongBotHandler, PongRandomHandler
from games.pong.models.pong_gestures import start_gesture_recognition


def define_sockets():
    return tornado.web.Application([
        (r"/ws/pong/", PongGesturesHandler),  # http://localhost:8001/ws/pong/
        (r"/ws/pong-bot/", PongBotHandler),  # http://localhost:8001/ws/pong-bot/
        (r"/ws/pong-random/", PongRandomHandler),  # http://localhost:8001/ws/pong-random/
    ])


if __name__ == "__main__":
    app = define_sockets()
    app.listen(8001)
    
    gest_thread = threading.Thread(target=start_gesture_recognition)
    gest_thread.start()
    
    tornado.ioloop.IOLoop.current().start()
    print("Started socket")
