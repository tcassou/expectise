from enum import Enum


class Lifespan(Enum):
    """
    Lifespan of a mock marker:
    * Permanent markers are not removed during tear down, only their mocks are reset.
    * Temporary markers are fully disabled during tear down, and removed from the session.
    """

    PERMANENT = "permanent"
    TEMPORARY = "temporary"
