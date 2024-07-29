# pylint: disable=redefined-outer-name

import pytest

from perp_simulation.entity.account import Account
from perp_simulation.use_case.settle_funding_rate_costs import SettleFundingRateCosts


@pytest.fixture
def settle_funding_rate_costs_use_case() -> SettleFundingRateCosts:
    return SettleFundingRateCosts()


def test_settle_funding_rate_costs_no_positions(
    settle_funding_rate_costs_use_case: SettleFundingRateCosts,
    account_100_no_positions: Account,
) -> None:
    result_account = settle_funding_rate_costs_use_case.settle(
        account_100_no_positions, 0.0001
    )
    assert result_account == account_100_no_positions


def test_settle_funding_rate_costs_positive_funding_rate(
    settle_funding_rate_costs_use_case: SettleFundingRateCosts,
    account_100_long_500usd: Account,
) -> None:
    result_account = settle_funding_rate_costs_use_case.settle(
        account_100_long_500usd, 0.0001
    )
    assert result_account.balance == 99.95
    assert len(result_account.positions[0].funding_rate_costs) == 1
    assert result_account.positions[0].funding_rate_costs[0] == 0.05


def test_settle_funding_rate_costs_negative_funding_rate(
    settle_funding_rate_costs_use_case: SettleFundingRateCosts,
    account_100_long_500usd: Account,
) -> None:
    result_account = settle_funding_rate_costs_use_case.settle(
        account_100_long_500usd, -0.0002
    )
    assert result_account.balance == 100.1
    assert len(result_account.positions[0].funding_rate_costs) == 1
    assert result_account.positions[0].funding_rate_costs[0] == -0.1
