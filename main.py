import os
import threading

import gym
from stable_baselines3 import DQN

from src.bot import PongBot
from src.enjoy import enjoy
from src.handlers import AiHandler
from src.socket import run_socket
from src.wrapper import StateStack


def main():
    env = gym.make('rag-2-ai/WebsocketPong-v0')
    env = StateStack(env, history_length=3)
    path = os.path.join(
        'trained-agents',
        'dqn',
        'WebsocketPong-v0',
        'WebsocketPong_200000_steps.zip'
    )
    model = DQN.load(path=path, env=env)
    routes = [
        (r"/ws/pong/", AiHandler, dict(env=env)),
        (r"/ws/pong-bot/", PongBot)
    ]
    socket_thread = threading.Thread(target=run_socket, args=(8001, routes))
    socket_thread.start()
    env.connection_event.wait()
    enjoy(model=model, env=env)


if __name__ == '__main__':
    main()
