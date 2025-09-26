class ExpectationError(Exception):
    """
    Error describing a mismatch between mock expectations and actual calls:
    * more or less calls than expected,
    * arguments passed to the mock do not match expectations.
    """
