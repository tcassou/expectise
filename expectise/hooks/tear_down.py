from expectise.lib.session import session


def tear_down():
    """Reset mocking behavior so that further tests can be run without any interference."""
    session.tear_down()
