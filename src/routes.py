import os

from typing import List, Tuple, Type
from stable_baselines3 import DQN
from src.env_sim.web_pong import prepare_pong_obs
from src.bots import PongBot
from src.handlers import AiHandler, RoutesHandler


def define_routes() -> List[Tuple[str, Type, dict]]:

    # DQN models path
    dqn_path = os.path.join('trained-agents', 'dqn')

    # DQN for specific game
    dqn_pong_path = os.path.join(
        dqn_path,
        'WebsocketPong-v0',
        'WebsocketPong_200000_steps.zip'
    )
    dqn_pong = DQN.load(path=dqn_pong_path)

    # Define routes
    routes = [
        (r"/ws/pong-dqn/", AiHandler, dict(
            model=dqn_pong,
            obs_funct=prepare_pong_obs,
            move_first=-1,
            move_last=1,
            history_length=3
        )),
        (r"/ws/pong-bot/", PongBot),
    ]
    endpoint = (r"/ws/routes/", RoutesHandler, dict(routes=routes))
    routes.append(endpoint)

    return routes
