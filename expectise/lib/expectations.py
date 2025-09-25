from .session import session


class Expectations:
    """
    Context manager for `Expect` statements.
    It can be used to check the set of expectations for any missing calls before exiting the context manager.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        session.tear_down(exception=exc_val)
