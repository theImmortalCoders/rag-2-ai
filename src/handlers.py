import json
import os
import socket
from urllib.parse import parse_qs, urlparse

import requests
from dotenv import load_dotenv
from tornado.websocket import WebSocketHandler


def verify_jwt(token):
    load_dotenv()
    TOKEN_VERIFY_URL = os.getenv('TOKEN_VERIFY_URL')
    headers = {"Authorization": "Bearer " + token}
    
    try:
        response = requests.get(TOKEN_VERIFY_URL, headers=headers)
        print(response)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"JWT verification failed: {e}")
        return False


class BaseHandler(WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        query_params = parse_qs(urlparse(self.request.uri).query)
        token = query_params.get("jwt", [None])[0]

        if not token or not verify_jwt(token):
            self.close(code=401, reason="Unauthorized")
            return
        print("WebSocket connection opened and authenticated")

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
