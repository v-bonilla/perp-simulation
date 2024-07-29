from dataclasses import asdict, dataclass
from typing import Dict, List, Literal, Optional

from perp_simulation.entity.account import Account
from perp_simulation.entity.account_snapshot import AccountSnapshot


@dataclass
class Simulation:
    """
    Represents a simulation in the trading system.
    """

    name: str
    simulation_start_ts: int
    simulation_end_ts: int
    timeframe: Literal["1m", "5m", "1h", "8h"]  # TODO: make enum
    symbol: str
    run_start_ts: Optional[int] = None
    run_end_ts: Optional[int] = None
    account_snapshots: Optional[List[Account]] = None

    def add_account_snapshot(self, account_snapshot: AccountSnapshot) -> None:
        """
        Adds an account snapshot to the simulation.
        """
        if self.account_snapshots is None:
            self.account_snapshots = []
        self.account_snapshots.append(account_snapshot)

    def to_dict(self) -> Dict:
        """
        Converts the simulation to a dictionary.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Simulation":
        """
        Creates a new simulation from a dictionary.
        """
        s = cls(**data)
        if s.account_snapshots:
            s.account_snapshots = [
                AccountSnapshot.from_dict(snapshot) for snapshot in s.account_snapshots
            ]
        return s
