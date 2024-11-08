import numpy as np

from collections import deque


def action_map(action: int, first: int, last: int) -> int:
    num_actions = last - first + 1
    return first + action % num_actions


def state_stack(obs: dict, states: deque) -> np.array:
    if len(states) == 0:
        for _ in range(states.maxlen):
            states.append(obs)
    else:
        states.append(obs)

    return np.array(states).flatten()
