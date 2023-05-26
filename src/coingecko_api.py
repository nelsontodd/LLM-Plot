import json
import utils
import requests
import math
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def fetch_trending_coins():
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    response = response.json()
    if 'status' in response.keys():
        print("Rate Limit Error: ")
        print(response)
        print("Reading from disk.")
        with open(utils.data_rel_path('trending.json'), "r") as f:
            loaded = json.load(f)
        trending_coins = loaded
    else:
        trending_coins = response["coins"]
        print("Writing to disk.")
        with open(utils.data_rel_path('trending.json'), "w") as f:
            json.dump(trending_coins, f)
    return trending_coins

def fetch_trending_coin_ids():
    trending_coins = fetch_trending_coins()
    return [coin["item"]["id"] for coin in trending_coins]

def coin_price_to_disk(coin_price, coin_id):
    with open(utils.data_rel_path('{}_price.json'.format(coin_id)), "w") as f:
        json.dump(coin_price, f)
    return 0

def coin_to_disk(coin_json, coin_id):
    with open(utils.data_rel_path('{}.json'.format(coin_id)), "w") as f:
        json.dump(coin_json, f)
    return 0

def coin_price_from_disk(coin_id):
    with open(utils.data_rel_path('{}_price.json'.format(coin_id)), "r") as f:
        price = json.load(f)
    return price

def coin_from_disk(coin_id):
    with open(utils.data_rel_path('{}.json'.format(coin_id)), "r") as f:
        coindata = json.load(f)
    return coindata

def get_coin_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url).json()
    if 'status' in response.keys():
        print("Rate Limit Error while pulling data for {}: ".format(coin_id))
        print(response)
        print("Reading from disk.")
        coindata = coin_from_disk(coin_id)
    else:
        coindata = response
        coin_to_disk(coindata, coin_id)
    return coindata

def get_coin_ids_list():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    coin_ids = response.json()
    with open(utils.data_rel_path('{}.json'.format("coin_ids")), "w") as f:
        json.dump(coin_ids, f)
    return 0

def fuzzy_find(s, strlist):

    def custom_scorer(s1, s2):
        if s1 == s2:
            return 100  # Max score for exact matches
        else:
            return fuzz.WRatio(s1, s2)

    return process.extractOne(s, strlist, scorer=custom_scorer)

def match_coin_id(coin_name):
    with open(utils.data_rel_path('{}.json'.format("coin_ids")), "r") as f:
        coin_ids = json.load(f)
    ids = [coin['id'] for coin in coin_ids]
    names = [coin['name'] for coin in coin_ids]
    symbols = [coin['symbol'] for coin in coin_ids]
    id_tuple = fuzzy_find(coin_name, ids)
    name_tuple = fuzzy_find(coin_name, names)
    symbol_tuple = fuzzy_find(coin_name, symbols)
    elem = max([id_tuple, name_tuple, symbol_tuple], key=lambda x: x[1])
    index = [*ids, *names, *symbols].index(elem[0])
    return coin_ids[index%len(ids)]['id']

def get_market_cap(coin_id):
    coin_data = get_coin_data(coin_id)
    market_cap = coin_data["market_data"]["market_cap"]["usd"]
    return market_cap

def handle_price_json(price_json):
    print(price_json.keys())
    data = price_json["prices"]
    df = pd.DataFrame(data, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms").dt.strftime('%m-%d-%y')
    print(df["timestamp"])
    return df

def historical_price(coin_id, pair="usd", days="30"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency={pair}&days={days}"
    response = requests.get(url).json()
    if 'status' in response.keys():
        print("Rate Limit Error while pulling historical price for {}: ".format(coin_id))
        print(response)
        print("Reading from disk.")
        prices = coin_price_from_disk(coin_id)
    else:
        prices = response
        coin_price_to_disk(prices, coin_id)
    return prices

