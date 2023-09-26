from .expect import Expect


class Expectations:
    """
    Class used as context manager for `Expect` statements, as a way to check the set of expectations
    for any missing calls before exiting tests.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        Expect.tear_down(exc_val)
