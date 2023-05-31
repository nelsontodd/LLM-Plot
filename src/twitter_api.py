import tweepy
import constants
import langplot

# fill these in with your API keys
consumer_key = constants.twitter_api_key
consumer_secret = constants.twitter_api_key_secret
access_token = constants.twitter_access_token
access_token_secret = constants.twitter_access_token_secret

import tweepy


prompt = "Plot the price of bitcoin and eth over the last day."
factory = langplot.PlotterFactory(prompt)
plotter = factory.create_plotter()
filename = plotter.plot()#"outputs/INSERT_USER_NAME_.png"

auth = tweepy.OAuth1UserHandler(
   constants.twitter_api_key, constants.twitter_api_key_secret,
   access_token, access_token_secret
)
api = tweepy.API(auth)
media = api.media_upload(filename)

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)
post_result = client.create_tweet(text=prompt, media_ids=[media.media_id])
