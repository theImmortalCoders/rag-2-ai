import json
import random

from Rag2WebsocketHandler import Rag2WebsocketHandler
from games.pong.models.pong_gestures import  get_move_from_gesture


class PongRandomHandler(Rag2WebsocketHandler):
    def send_data(self, receivedData):
        move = random.choice([-1, 0, 1])
        self.write_message(json.dumps({'move': move}))

class PongBotHandler(Rag2WebsocketHandler):
    def send_data(self, data):
        if data['playerId'] == 0:
            if data['state']['ballY'] < data['state']['leftPaddleY'] + 50:
                move = 1
            else:
                move = -1
        else:
            if data['state']['ballY'] < data['state']['rightPaddleY'] + 50:
                move = 1
            else:
                move = -1
        self.write_message(json.dumps({'move': move}))

class PongGesturesHandler(Rag2WebsocketHandler):
    def send_data(self, receivedData):
        move = get_move_from_gesture()
        self.write_message(json.dumps({'move': move}))
