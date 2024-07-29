from dataclasses import dataclass

from perp_simulation.entity.account import Account


@dataclass
class AccountSnapshot:
    """Represents a snapshot of an account at a specific time."""

    ts: int
    account: Account

    @classmethod
    def from_dict(cls, data: dict) -> "AccountSnapshot":
        """Creates a new account snapshot from a dictionary."""
        return cls(ts=data["ts"], account=Account.from_dict(data["account"]))
