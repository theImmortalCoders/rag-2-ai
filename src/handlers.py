import json
from tornado.websocket import WebSocketHandler


class BaseHandler(WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket connection opened")

    def on_close(self):
        print("WebSocket connection closed")

    def on_message(self, message):
        pass


class AiHandler(BaseHandler):

    def initialize(self, env):
        self.env = env

    def on_message(self, message):
        data = json.loads(message)
        self.env.update_observation(data)
        move = self.env.return_move()
        if move is not None:
            self.write_message(json.dumps({'move': move}))
