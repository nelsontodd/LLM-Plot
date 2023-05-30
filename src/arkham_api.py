import json
import time
import requests
import math
import pandas as pd
import utils
import constants
import requests
from datetime import datetime
from functools import reduce

def get_transfers_endpoint(base, flow='all', from_address=None):
    base_url = 'https://api.arkhamintelligence.com/transfers'
    params = {
        'base': base,
        'flow': flow
    }
    headers = {
            'API-Key': constants.arkham_api_key
            }
    if from_address:
        params['from'] = from_address
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("fail {}".format(response))
        return None

def get_portfolio_endpoint(address_or_entity):
    now = datetime.now()
    timestamp = int(time.mktime(now.timetuple()))*1000
    if len(address_or_entity) != 42 or "0x" != address_or_entity[0:2]:
        base_url = 'https://api.arkhamintelligence.com/portfolio/entity/{}?time={}'.format(address_or_entity, timestamp)
    else:
        base_url = 'https://api.arkhamintelligence.com/portfolio/address/{}?time={}'.format(address_or_entity, timestamp)
    headers = {
            'API-Key': constants.arkham_api_key
            }
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("fail {}".format(response.json()))
        return None

def arkham_to_pd(historical):
    dfs = {}
    for chain in historical.keys():
        df = pd.DataFrame()
        df['value'] = [elem['usd'] for elem in historical[chain]]
        df.index = [elem['time'] for elem in historical[chain]]
        if df.empty == False:
            dfs[chain] = df
    return dfs

def historical_balance(address_or_entity, chain='all'):
    dfs = arkham_to_pd(get_historical_endpoint(address_or_entity))
    if chain == 'all':
        if len(dfs.keys()) > 1:
            result = reduce(lambda a, b: a.add(b, fill_value=0),list(dfs.values()))
        else:
            result = list(dfs.values())[0]
    else:
        try:
            result = dfs[chain]
        except KeyError as e:
            print(e)
            result = list(dfs.values())[0]
    print(result)
    return result

def get_historical_endpoint(address_or_entity, entity=False):
    #if len(address_or_entity) != 42 or "0x" != address_or_entity[0:2]:
        #base_url = 'https://api.arkhamintelligence.com/history/entity/{}'.format(address_or_entity)
    #else:
    base_url = 'https://api.arkhamintelligence.com/history/address/{}'.format(address_or_entity)
    headers = {
            'API-Key': constants.arkham_api_key
            }
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("fail {}".format(response.json()))
        return None
