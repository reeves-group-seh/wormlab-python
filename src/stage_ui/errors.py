class InvalidStateError(Exception):
    """
    Raised when an invalid state is reached. This indicates a logic bug and
    means the program has reached a state that should not be possible. The
    program should most likely crash if this error is seen.
    """

    pass
