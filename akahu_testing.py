import os
import sys
from pprint import pprint  # NOQA
import json

import pandas as pd

import requests
import yfinance as yf

headers = {
    "Authorization": f"Bearer {os.environ.get('token')}",
    "X-Akahu-Id": os.environ.get("akahu_id"),
}
res = requests.get("https://api.akahu.io/v1/accounts", headers=headers)

res_json = res.json()
if not res_json["success"]:
    sys.exit(1)

items = res_json["items"]
accounts = {}

for item in items:
    if item["connection"]["name"] not in accounts:
        accounts[item["connection"]["name"]] = [item]
    else:
        accounts[item["connection"]["name"]] += [item]

sharesies_portfolio_verbose = accounts["Sharesies"][0]["meta"]["portfolio"]


sharesies_portfolio = {}
for share in sharesies_portfolio_verbose:
    if share["currency"] == "NZD":
        sharesies_portfolio[share["symbol"]+".NZ"] = share["shares"]
    else:
        sharesies_portfolio[share["symbol"]] = share["shares"]

data = pd.DataFrame()

for ticker in sharesies_portfolio:
    data[ticker] = yf.download(ticker, period="2y")["Adj Close"]

data = data.ffill()
recent_prices = json.loads(data.iloc[-1,:].to_json())

portfolio_value = {
    ticker: sharesies_portfolio[ticker] * recent_prices[ticker] for ticker in recent_prices
}

pprint(portfolio_value)