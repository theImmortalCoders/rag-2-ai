import logging
from threading import Event

import numpy as np
from gym import Env
from gym.spaces import Box, Discrete

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')


class WebsocketPong(Env):
    def __init__(self):
        super().__init__()
        self.name = "WebsocketPong"
        self.action_space = Discrete(3)

        self.min_values = np.array([0, 0, 0, 0, -100, -100], dtype=np.float32)
        self.max_values = np.array([600, 600, 1000, 600, 100, 100], dtype=np.float32)

        self.observation_space = Box(
            low=np.array([0, 0, 0, 0, -1, -1], dtype=np.float32),
            high=np.array([1, 1, 1, 1, 1, 1], dtype=np.float32),
            dtype=np.float32
        )

        self.norm_observation = np.array([-2, 2, -2, 2, -2, 2], dtype=np.float32)

        self.playerId = None
        self.prevScoreLeft = self.internalLeftScore = 0
        self.prevScoreRight = self.internalRightScore = 0

        self.state = None
        self.first_step = True
        self.new_obs_event = Event()
        self.new_move_event = Event()

        self.is_connected = False
        self.connection_event = Event()
        self.move = 0

        self.prev_observation = None
        self.repetition_count = 0

    def update_observation(self, data):
        self.state = data['state']

        # if self.playerId is None:
        self.playerId = data['playerId']

        if self.playerId == 0:
            curr_observation = np.array([
                self.state['leftPaddleY'],
                self.state['rightPaddleY'],
                self.state['ballX'],
                self.state['ballY'],
                self.state['ballSpeedX'],
                self.state['ballSpeedY'],
            ], dtype=np.float32)
        else:
            curr_observation = np.array([
                self.state['rightPaddleY'],
                self.state['leftPaddleY'],
                1000 - self.state['ballX'],
                self.state['ballY'],
                -self.state['ballSpeedX'],
                self.state['ballSpeedY'],
            ], dtype=np.float32)

        self.norm_observation[:4] = ((curr_observation[:4] - self.min_values[:4]) /
                                     (self.max_values[:4] - self.min_values[:4]))

        self.norm_observation[4:] = 2 * ((curr_observation[4:] - self.min_values[4:]) /
                                         (self.max_values[4:] - self.min_values[4:])) - 1

        self.new_obs_event.set()
        if not self.is_connected:
            self.is_connected = True
            self.connection_event.set()

    def get_observation(self):
        self.new_obs_event.wait()
        self.new_obs_event.clear()
        return self.norm_observation

    def log_repeated_observation(self, observation, method: str):
        if self.prev_observation is not None and np.array_equal(observation, self.prev_observation):
            self.repetition_count += 1
            logging.warning("Repeated observation #%d in method %s", self.repetition_count, method)

        self.prev_observation = observation.copy()

    def get_done(self):
        if self.internalLeftScore == 10 or self.internalRightScore == 10:
            self.internalLeftScore = self.internalRightScore = 0
            return True
        return False

    def reset(self):
        if self.first_step:
            self.first_step = False
        else:
            self.move = 0
            self.new_move_event.set()
        self.internalLeftScore = self.internalRightScore = 0
        observation = self.get_observation()
        self.log_repeated_observation(observation, "reset")
        self.prevScoreLeft = self.state['scoreLeft']
        self.prevScoreRight = self.state['scoreRight']
        return observation

    def step(self, action):
        action_map = {0: -1, 1: 0, 2: 1}
        self.move = action_map[action]
        self.new_move_event.set()

        observation = self.get_observation()

        self.log_repeated_observation(observation, "step")

        done = self.get_done()
        reward = 0
        if self.playerId == 0:
            if self.state['scoreLeft'] > self.prevScoreLeft:
                self.internalLeftScore += 1
                self.prevScoreLeft = self.state['scoreLeft']
            elif self.state['scoreRight'] > self.prevScoreRight:
                self.internalRightScore += 1
                self.prevScoreRight = self.state['scoreRight']
                reward = -10
        else:
            if self.state['scoreRight'] > self.prevScoreRight:
                self.internalRightScore += 1
                self.prevScoreRight = self.state['scoreRight']
            elif self.state['scoreLeft'] > self.prevScoreLeft:
                self.internalLeftScore += 1
                self.prevScoreLeft = self.state['scoreLeft']
                reward = -10

        info = {}
        return observation, reward, done, info

    def return_move(self):
        self.new_move_event.wait()
        self.new_move_event.clear()
        return self.move

    def render(self):
        pass

    def close(self):
        pass
