"""Library exceptions."""


class MissingRequiredArgumentError(Exception):
    """There is a missing argument in query."""


class UnusedArgumentsError(Exception):
    """There are unused arguments in query."""
