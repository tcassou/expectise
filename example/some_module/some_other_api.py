# -*- coding: utf-8 -*-


class SomeOtherAPI:
    def __init__(self, foo: int = 1) -> None:
        self.foo = foo

    def do_advanced_stuff(self, bar: str) -> str:
        print("Performing advanced things")
        return f"{bar}>>{self.foo}"
