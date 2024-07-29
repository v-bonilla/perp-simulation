# pylint: disable=missing-class-docstring
"""Define expections in the system."""

class InsufficientBalanceError(Exception):
    def __init__(self):
        super().__init__("Not enough available balance to perform the requested operation.")
