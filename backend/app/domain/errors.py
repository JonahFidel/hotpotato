class InvalidConfig(ValueError):
    """The game cannot be created or patched with the given settings."""


class IllegalTransition(ValueError):
    """A move was attempted that the current phase does not allow."""
