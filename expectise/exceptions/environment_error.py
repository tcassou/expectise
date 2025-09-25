class EnvironmentError(Exception):
    """
    Error describing the wrong environment setup, typically arising from
    * not setting the correct envionment variable, according to `mock_if` decorations,
    * not marking methods as mocked with the `mock_if` decorator,
    * defining incomplete `Expect` statements.
    """
