from .expect import Expect


class Expectations:
    """
    Class used as context manager for `Expect` statements, as a way to check the set of expectations
    for any missing calls before exiting tests.
    """

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        Expect.tear_down()
