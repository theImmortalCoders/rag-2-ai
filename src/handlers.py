import json
import os
from urllib.parse import parse_qs, urlparse

import numpy as np
import requests
from dotenv import load_dotenv
from tornado.websocket import WebSocketHandler
from stable_baselines3.common.base_class import BaseAlgorithm
from src.env_sim.general import state_stack, action_map
from tornado.web import RequestHandler
from typing import List, Tuple, Type, Callable
from collections import deque


def verify_jwt(token):
    load_dotenv()
    TOKEN_VERIFY_URL = os.getenv('TOKEN_VERIFY_URL')
    headers = {"Authorization": "Bearer " + token}
    
    try:
        response = requests.get(TOKEN_VERIFY_URL, headers=headers, timeout=2)
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

    def initialize(
            self,
            model: BaseAlgorithm,
            obs_funct: Callable[[dict], np.array],
            move_first: int,
            move_last: int,
            history_length: int = 1
    ):
        if history_length < 1:
            raise ValueError("history_length must be an integer greater than or equal to 1")

        self.model = model
        self.prepare_obs = obs_funct
        self.states = deque(maxlen=history_length)
        self.move_first = move_first
        self.move_last = move_last

    def on_close(self):
        self.states.clear()
        print("WebSocket connection closed")

    def on_message(self, message):
        data = json.loads(message)
        obs = self.prepare_obs(data)
        obs = state_stack(obs=obs, states=self.states)
        action, _states = self.model.predict(
            observation=obs,
            deterministic=True
        )
        move = action_map(
            action=int(action),
            first=self.move_first,
            last=self.move_last
        )
        if move is not None:
            self.write_message(json.dumps({'move': move}))


class RoutesHandler(RequestHandler):
    def set_default_headers(self):
        load_dotenv()
        self.set_header("Access-Control-Allow-Origin", os.getenv("ALLOWED_ORIGINS"))
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, Authorization")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        self.set_status(204)
        self.finish()

    def initialize(self, routes: List[Tuple[str, Type, dict]]):
        self.routes = routes

    def get(self):
        routes_info = [{"path": route[0], "name": route[1].__name__} for route in self.routes]
        self.write(json.dumps(routes_info))
