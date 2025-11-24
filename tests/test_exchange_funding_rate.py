import pytest
from unittest.mock import Mock, patch

from alphaloop.market.exchange import BinanceClient


@patch("alphaloop.market.exchange.ccxt.binanceusdm")
def test_fetch_funding_rate_prefers_predicted(mock_binanceusdm):
    """BinanceClient should return predictedFundingRate when available."""
    mock_ex = Mock()
    mock_ex.load_markets.return_value = {"ETH/USDT:USDT": {"id": "ETHUSDT"}}
    mock_ex.fapiPublicGetPremiumIndex.return_value = {
        "symbol": "ETHUSDT",
        "predictedFundingRate": "0.0000212",
        "lastFundingRate": "0.0000100",
    }
    mock_binanceusdm.return_value = mock_ex

    client = BinanceClient()
    rate = client.fetch_funding_rate()

    assert rate == pytest.approx(0.0000212)


@patch("alphaloop.market.exchange.ccxt.binanceusdm")
def test_fetch_funding_rate_falls_back_to_last(mock_binanceusdm):
    """If predictedFundingRate is missing, fall back to lastFundingRate."""
    mock_ex = Mock()
    mock_ex.load_markets.return_value = {"ETH/USDT:USDT": {"id": "ETHUSDT"}}
    mock_ex.fapiPublicGetPremiumIndex.return_value = {
        "symbol": "ETHUSDT",
        "predictedFundingRate": None,
        "lastFundingRate": "0.0000333",
    }
    mock_binanceusdm.return_value = mock_ex

    client = BinanceClient()
    rate = client.fetch_funding_rate()

    assert rate == pytest.approx(0.0000333)


