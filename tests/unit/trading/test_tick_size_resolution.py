from src.trading.hyperliquid_client import HyperliquidClient


def _make_client_with_meta(meta):
    client = HyperliquidClient.__new__(HyperliquidClient)
    # Minimal attributes needed by _resolve_tick_size
    client._fetch_meta_data = lambda: meta
    return client


def test_tick_size_uses_price_increment():
    meta = {"universe": [{"name": "BTC", "priceIncrement": 0.5}]}
    client = _make_client_with_meta(meta)

    tick = client._resolve_tick_size("BTC")
    assert tick == 0.5


def test_tick_size_uses_px_decimals():
    meta = {"universe": [{"name": "ETH", "pxDecimals": 2}]}
    client = _make_client_with_meta(meta)

    tick = client._resolve_tick_size("ETH")
    assert tick == 10 ** (-2)


def test_tick_size_from_orderbook_gap_when_meta_missing():
    meta = {"universe": [{"name": "BTC"}]}
    client = _make_client_with_meta(meta)

    tick = client._resolve_tick_size(
        "BTC", {"best_bid": 100.0, "best_ask": 100.5}
    )
    assert tick == 0.5


def test_tick_size_defaults_by_coin_when_no_meta_or_snapshot():
    client = _make_client_with_meta(None)
    assert client._resolve_tick_size("BTC") == 0.5
    assert client._resolve_tick_size("ETH") == 0.1
    assert client._resolve_tick_size("DOGE") == 0.1
