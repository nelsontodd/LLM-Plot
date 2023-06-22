import os
import time
import json
import requests
import openai
from . import constants
import tiktoken
import math
twitter = "https://api.twitter.com{}"

def output_rel_path(filename, extension=""):
    return constants.output_path+filename+extension

def data_rel_path(filename, extension=""):
    return constants.data_path+filename+extension

def num_tokens_from_messages(prompttext, model="gpt-3.5-turbo-0301"):
  """Returns the number of tokens used by a list of messages."""
  messages = [{"role":"user", "content":prompttext}]
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

def promptGPT(systemprompt, userprompt, model=constants.model):
    print("""Inputting {} tokens into {}.""".format(num_tokens_from_messages(systemprompt+userprompt), model))
    response = openai.ChatCompletion.create(
      model=model,
      messages=[
        {"role": "system", "content": systemprompt},
        {"role": "user", "content": userprompt}])
    return response["choices"][0]["message"]["content"]

def find_values(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find_values(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict):
                    for result in find_values(key, d):
                        yield result

def round_nearest_billion(x):
    return int(math.ceil(x / 1000000000.0)) * 1000000000

def custom_currency_formatter(x):
    if x < 1:
        return f"${x*100:.00f} cents"
    elif x < 1000:
        return f"${x:.0f}"
    elif x < 1000000:
        return f"${x / 1000:.0f}k"
    elif x < 1000000000:
        return f"${x / 1000000:.0f}M"
    else:
        return f"${x / 1000000000:.0f}B"

def find_values(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find_values(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict):
                    for result in find_values(key, d):
                        yield result

def twitter_request(url,params={}):
    print("Making Twitter API Request to {}.".format(url))
    response = requests.get(url, headers={'Authorization':
            'Bearer {}'.format(constants.twitter_bearer_token)}, params=params)
    return response.json()

def get_tweets_by_id(uid,max_results=10):
    endpoint = "/2/users/{}/tweets".format(uid)
    return twitter_request(twitterurlbase.format(endpoint), params={'max_results':str(max_results)})

def get_wallet_tokens(api_key, wallet_address):
    endpoint = f"https://api.etherscan.io/api?module=account&action=tokentx&address={wallet_address}&startblock=0&endblock=999999999&sort=asc&apikey={api_key}"
    response = requests.get(endpoint)
    if response.status_code == 200:
        transactions = response.json().get('result')
        tokens = set()
        for transaction in transactions:
            tokens.add(transaction['tokenSymbol'])
        return list(tokens)
    else:
        return None

def retrieve_id(username: str):
    endpoint = "/2/users/by/username/{}"
    with open(output_rel_path("twitter_user_ids.json"), "r") as f:
        idlist = json.load(f)
    try:
        uid = idlist[username]
    except Exception as e:
        uid = twitter_request(twitterurlbase.format(endpoint.format(username)))['data']['id']
        idlist.update({"{}".format(username):"{}".format(uid)})
        with open(output_rel_path("twitter_user_ids.json"), "w") as f:
            json.dump(idlist, f)
    return uid

def get_tweet_text_from_ids(ids, granularity='%Y-%m-%d %H', max_results=10, file=''):
    if file != '':
        with open(output_rel_path(file), "r") as f:
            tweets = json.load(f)
        tweet_text = []
        for tweet in tweets:
            tweet_text.append(list(find_values("text",tweet)))
        return tweet_text
    try:
        with open(output_rel_path("user_tweets_{}.json".format(datetime.datetime.now().strftime(granularity))), "r") as f:
            tweets = json.load(f)
    except Exception as e:
        tweets = []
        for uid in ids:
            utweets = get_tweets_by_id(uid, max_results=max_results)
            tweets.append(utweets)
        with open(output_rel_path("user_tweets_{}.json".format(datetime.datetime.now().strftime(granularity))), "w") as f:
            json.dump(tweets, f)
    tweet_text = []
    for tweet in tweets:
        tweet_text.append(list(find_values("text",tweet)))
    return tweet_text
