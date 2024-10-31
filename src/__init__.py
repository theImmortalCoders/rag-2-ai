from gym.envs.registration import register

register(
    id='rag-2-ai/WebsocketPong-v0',
    entry_point='src.envs:WebsocketPong',
)
