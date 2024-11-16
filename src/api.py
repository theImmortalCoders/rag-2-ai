import json
import os
from typing import List, Tuple, Type
from urllib.parse import urlparse, parse_qs

import requests
from dotenv import load_dotenv
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

guest_users = 0


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
    is_guest = False

    def check_origin(self, origin):
        return True

    def open(self):
        global guest_users

        query_params = parse_qs(urlparse(self.request.uri).query)
        token = query_params.get("jwt", [None])[0]
        load_dotenv()
        ALLOWED_GUEST_USERS = os.getenv('ALLOWED_GUEST_USERS')

        if not token or not verify_jwt(token):
            if guest_users >= int(ALLOWED_GUEST_USERS):
                print("Max guest limit exceeded")
                self.close(code=401, reason="Unauthorized")
                return
            guest_users += 1
            self.is_guest = True
            print("WebSocket connection opened as guest")
        else:
            print("WebSocket connection opened and authenticated")

    def on_close(self):  # always call when overload
        global guest_users

        if self.is_guest:
            guest_users -= 1
            print(f"Guest user disconnected. Remaining guest users: {guest_users}")
        else:
            print("Authenticated user disconnected")

        print("WebSocket connection closed")

    def on_message(self, message):
        pass


class RoutesHandler(RequestHandler):
    routes = []
    
    def set_default_headers(self):
        load_dotenv()
        allowed_origins = os.getenv("ALLOWED_ORIGINS").split(',')

        origin = self.request.headers.get("Origin")
        if origin in allowed_origins:
            self.set_header("Access-Control-Allow-Origin", origin)
        else:
            self.set_header("Access-Control-Allow-Origin", "null")

        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, Authorization")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def options(self):
        self.set_status(204)
        self.finish()

    def initialize(self, routes: List[Tuple[str, Type, dict]]):
        self.routes = routes

    def get(self):
        routes_info = []
        for route in self.routes:
            path = route[0][:-1]
            last_dash_index = path.rfind('-')
            last_slash_index = path.rfind('/')
            last_index = max(last_dash_index, last_slash_index)

            if last_index != -1:
                url_type = path[last_index + 1:].upper()
            else:
                url_type = path.upper()

            routes_info.append({"path": route[0], "name": url_type})

        self.write(json.dumps(routes_info))
