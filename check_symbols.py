import ccxt
from config import API_KEY, API_SECRET

exchange = ccxt.binanceusdm(
    {"apiKey": API_KEY, "secret": API_SECRET, "options": {"defaultType": "future"}}
)
exchange.urls["api"] = {
    "fapiPublic": "https://testnet.binancefuture.com/fapi/v1",
    "fapiPrivate": "https://testnet.binancefuture.com/fapi/v1",
}
exchange.has["fetchCurrencies"] = False
exchange.load_markets()
print("Available symbols:")
for s in exchange.markets:
    if "USDT" in s:
        print(s)
