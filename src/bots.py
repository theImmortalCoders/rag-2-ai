import json
import random
from turtledemo.chaos import jumpto

from six import moves

from src.handlers import BaseHandler


class PongBot(BaseHandler):
    def send_message(self, message):
        data = json.loads(message)

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

        self.write_message(json.dumps({'move': move, 'start': 1}))

class FlappybirdBot(BaseHandler):
    def send_message(self, message):
        data = json.loads(message)['state']
        jump = 0
       
        if not data['isGameStarted']:
            jump = 1
        else:
            obstacles = data['obstacles']
            lowestDist = 1000
            lowestDistIndex = 0
            for i in range(0, len(obstacles)):
                dist = obstacles[i]['distanceX']
                if lowestDist > dist > 60:
                    lowestDist = dist
                    lowestDistIndex = i
            
            if data['birdY'] > obstacles[lowestDistIndex]['centerGapY']:
                jump = 1

        self.write_message(json.dumps({'jump': jump}))
