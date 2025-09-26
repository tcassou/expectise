class SomeOtherAPI:
    def __init__(self, foo: int = 1) -> None:
        self.foo = foo

    def do_advanced_stuff(self, bar: str) -> str:
        print("Performing advanced things")
        return f"{bar}>>{self.foo}"

    @property
    def secret_info(self) -> str:
        return "P@55W0RD"
