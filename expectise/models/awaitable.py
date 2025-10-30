import asyncio


class Awaitable:
    def __init__(self, value):
        self.value = value

    def __await__(self):
        future = asyncio.Future()
        future.set_result(self.value)
        return future.__await__()
