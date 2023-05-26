import os
import time
import json
import requests
import openai
import constants
import tiktoken
import math

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
