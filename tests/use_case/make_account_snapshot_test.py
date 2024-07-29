# pylint: disable=redefined-outer-name
from datetime import datetime

import pytest

from perp_simulation.entity.account import Account
from perp_simulation.use_case.make_account_snapshot import MakeAccountSnapshot


@pytest.fixture
def make_account_snapshot_use_case() -> MakeAccountSnapshot:
    return MakeAccountSnapshot()


def test_make_account_snapshot_account_no_positions(
    make_account_snapshot_use_case: MakeAccountSnapshot,
    account_100_no_positions: Account,
):
    # TODO: Change to UTC
    ts = datetime.fromisoformat("2024-01-01T00:00:00").timestamp()
    account_snapshot = make_account_snapshot_use_case.make(
        account=account_100_no_positions, ts=ts
    )
    assert account_snapshot.ts == ts
    assert account_snapshot.account.positions is None
    assert account_snapshot.account == account_100_no_positions


def test_make_account_snapshot_account_one_position(
    make_account_snapshot_use_case: MakeAccountSnapshot,
    account_100_long_500usd: Account,
):
    # TODO: Change to UTC
    ts = datetime.fromisoformat("2024-03-01T00:00:00").timestamp()
    account_snapshot = make_account_snapshot_use_case.make(
        account=account_100_long_500usd, ts=ts
    )
    assert account_snapshot.ts == ts
    assert len(account_snapshot.account.positions) == 1
    assert account_snapshot.account == account_100_long_500usd
