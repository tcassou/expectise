from os import environ


class Trigger:
    pass


class EnvTrigger(Trigger):
    def __init__(self, env_key: str, env_val: str):
        self.env_key = env_key
        self.env_val = env_val

    def is_met(self) -> bool:
        return environ.get(self.env_key, "") == self.env_val


class AlwaysTrigger(Trigger):
    def is_met(self) -> bool:
        return True
