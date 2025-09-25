from os import environ


class Trigger:
    pass


class EnvTrigger(Trigger):
    """Trigger to activate a mock marker only when the environment variable is set to a specific value."""

    def __init__(self, env_key: str, env_val: str):
        self.env_key = env_key
        self.env_val = env_val

    def is_met(self) -> bool:
        return environ.get(self.env_key, "") == self.env_val


class AlwaysTrigger(Trigger):
    """Trigger to activate a mock marker regardless of the environment."""

    def is_met(self) -> bool:
        return True
