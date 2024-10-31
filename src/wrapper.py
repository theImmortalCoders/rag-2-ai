from collections import deque

import numpy as np
from gym import Env
from gym import Wrapper
from gym.spaces import Box


class StateStack(Wrapper):
    def __init__(self, env: Env, history_length: int = 3):
        super().__init__(env)
        self.history_length = history_length
        self.frames = deque(maxlen=history_length)
        low = np.repeat(env.observation_space.low[np.newaxis, ...], history_length, axis=0)
        high = np.repeat(env.observation_space.high[np.newaxis, ...], history_length, axis=0)
        self.observation_space = Box(low=low.flatten(), high=high.flatten(), dtype=env.observation_space.dtype)

    def reset(self):
        observation = self.env.reset()
        for _ in range(self.history_length):
            self.frames.append(observation)
        return self._get_observation()

    def step(self, action):
        observation, reward, done, info = self.env.step(action)
        self.frames.append(observation)
        return self._get_observation(), reward, done, info

    def _get_observation(self):
        return np.array(self.frames).flatten()
