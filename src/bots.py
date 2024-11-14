import json

from src.handlers import BaseHandler


class PongBot(BaseHandler):
    def on_message(self, message):
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
