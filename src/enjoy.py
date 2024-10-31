from gym import Env
from stable_baselines3.common.base_class import BaseAlgorithm


def enjoy(model: BaseAlgorithm, env: Env, num_episodes: int = 5) -> None:
    for episode in range(num_episodes):
        obs = env.reset()
        done = False

        while not done:
            action, _states = model.predict(observation=obs, deterministic=True)
            obs, reward, done, info = env.step(int(action))
