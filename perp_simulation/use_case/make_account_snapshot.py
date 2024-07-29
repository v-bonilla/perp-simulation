import logging
from copy import deepcopy

from perp_simulation.entity.account import Account
from perp_simulation.entity.account_snapshot import AccountSnapshot


class MakeAccountSnapshot:
    """Make a snapshot of the account.

    - Actor: User
    - Scenario:
        1. The system retrieves the current ts. For the moment, it's an argument.
        2. Make a recursive copy of the account.
        3. The system returns the snapshot.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def make(self, account: Account, ts: float) -> AccountSnapshot:
        """Make a snapshot of the account.

        Args:
            account (Account): The account.
            ts (float): The timestamp.

        Returns:
            AccountSnapshot: The account snapshot.
        """
        self.logger.info("Making account snapshot.")
        account_copy = deepcopy(account)
        account_snapshot = AccountSnapshot(ts=ts, account=account_copy)
        self.logger.info("Account snapshot made: %s", account_snapshot)
        return account_snapshot
