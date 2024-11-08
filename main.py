import os

from stable_baselines3 import DQN
from src.env_sim.web_pong import prepare_pong_obs
from src.bot import PongBot
from src.handlers import AiHandler, RoutesHandler
from src.socket import run_socket


def main():
    path = os.path.join(
        'trained-agents',
        'dqn',
        'WebsocketPong-v0',
        'WebsocketPong_200000_steps.zip'
    )
    model = DQN.load(path=path)
    routes = [
        (r"/ws/pong/", AiHandler, dict(
            model=model,
            obs_funct=prepare_pong_obs,
            move_first=-1,
            move_last=1,
            history_length=3
        )),
        (r"/ws/pong-bot/", PongBot),
    ]
    endpoint = (r"/ws/routes/", RoutesHandler, dict(routes=routes))
    routes.append(endpoint)
    run_socket(port=8001, routes=routes)


if __name__ == '__main__':
    main()
