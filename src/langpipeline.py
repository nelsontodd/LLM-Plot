import pandas as pd
import numpy as np
import json
import utils
import constants
import requests
import coingecko_api
from datetime import timedelta
import matplotlib 
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import random

class WalletViz:

    def __init__(self, prompt, model="gpt-3.5-turbo"):
        self.initprompt = prompt
        self.model=model
        self.json = self.parse_input(prompt)
        self.plot_type = self.json['PLOT_TYPE']
        self.plot_duration = self.json['PLOT_DURATION']
        self.were_dates_specified = self.json['SPECIFIC_DATES_SPECIFIED']
        self.plot_dates = self.json['PLOT_DATES']
        self.assets = self.json['ASSETS']
        self.required_asset_data = self.json['REQUIRED_ASSET_DATA']
        self.user_owns_asset = self.json['USER_OWNS_ASSET']

    def reformat(self, instructions_json):
        if type(instructions_json['PLOT_DURATION']) == str:
            instructions_json['PLOT_DURATION'] = eval(instructions_json['PLOT_DURATION']) #Security risk
        if type(instructions_json['REQUIRED_ASSET_DATA']) == str:
            instructions_json['REQUIRED_ASSET_DATA'] = [instructions_json['REQUIRED_ASSET_DATA']]
        if type(instructions_json['SPECIFIC_DATES_SPECIFIED']) == str:
            instructions_json['SPECIFIC_DATES_SPECIFIED'] = eval(instructions_json['SPECIFIC_DATES_SPECIFIED'])
        if type(instructions_json['USER_OWNS_ASSET']) == str:
            instructions_json['USER_OWNS_ASSET'] = eval(instructions_json['USER_OWNS_ASSET'])
        if type(instructions_json['ASSETS']) == str:
            instructions_json['ASSETS'] = [instructions_json['ASSETS']]
        if 'ether' in list(map(lambda x: x.lower(), instructions_json['ASSETS'])):
            instructions_json['ASSETS'][list(map(lambda x: x.lower(), instructions_json['ASSETS'])).index('ether')] = 'ETH'
        return instructions_json

    def parse_input(self, prompt):
        instructions_json = json.loads(utils.promptGPT(constants.INSTRUCTIONS_JSON,
            prompt, self.model))
        instructions_json = self.reformat(instructions_json)
        instructions_json['ASSETS'] = list(map(lambda x: coingecko_api.match_coin_id(x),
            instructions_json['ASSETS']))
        return instructions_json

    def fetch_data(self):
        if self.user_owns_asset == True:
            return self.get_wallet_data()
        elif self.user_owns_asset == False:
            return self.get_coingecko_data()
        else:
            return "USER_OWNS_ASSET Ambiguous"

    def get_coingecko_data(self):
        data_points = {}
        def get_asset_data_from_coingecko(asset, data):
            if data == "PRICE":
                return coingecko_api.handle_price_json(coingecko_api.historical_price(asset,
                    days=str(self.plot_duration.days)))
            if data == "TOKEN SUPPLY":
                return coingecko_api.handle_price_json(coingecko_api.historical_supply(asset))
            if data == "MARKETCAP":
                return coingecko_api.handle_price_json(coingecko_api.historical_marketcap(asset))

        for asset in self.assets:
            data_points[asset] = {}
            for data in self.required_asset_data:
                data_points[asset][data] = get_asset_data_from_coingecko(asset, data)
        return data_points

    def timeseries_plot(self):

        def random_color():
            # Generate random RGB values between 0 and 255
            random.seed()
            r = random.randint(0, 255)/255
            g = random.randint(0, 255)/255
            b = random.randint(0, 255)/255
            # Return the color as a tuple
            return (r, g, b)

        asset_data = self.fetch_data()
        assetstr = "of "
        fig, ax1 = plt.subplots()
        for index,asset in enumerate(asset_data.keys()):
            if index == 0:
                assetstr += asset
            else:
                assetstr += " and "+asset
            if "PRICE" in asset_data[asset].keys():
                price = asset_data[asset]["PRICE"]
                priceax = ax1.twinx()
                xticks = np.linspace(0,len(price.index)-1, 5)
                num_decimals = str(price['price'].iloc[-1])[::-1].find('.')
                formatter = ticker.FuncFormatter(lambda x, pos:
                        '${:,.{prec}f}'.format(x,prec=num_decimals))
                #yticks = np.linspace(0,len(price['price'])-1, 5)
                xticklabels = [price["timestamp"].iloc[int(tick)] for tick in xticks]
                #yticklabels = [utils.custom_currency_formatter(y) for y in yticks]
                color = random_color()
                priceax.plot(price.index, price['price'], color=color, label ="""{}
                        price""".format(asset))
                priceax.yaxis.set_major_formatter(formatter)
                priceax.tick_params(axis='y', colors=color)
            if "TOKEN SUPPLY" in asset_data[asset].keys():
                supply = asset_data[asset]["TOKEN SUPPLY"]
                supply.plot(kind='line')
            if "MARKETCAP" in asset_data[asset].keys():
                marketcap = asset_data[asset]["MARKETCAP"]
                marketcap.plot(kind='line')
            if "QTY HELD " in asset_data[asset].keys():
                qtyheld = asset_data[asset]["QTY HELD"]
                qtyheld.plot(kind='line')
                # Adjust spacing between subplots
        fig.tight_layout()
        fig.legend(loc='upper left')
        plt.xticks(xticks, xticklabels,rotation=45, ha="right")
        plt.title("{} {}".format(self.required_asset_data,
            assetstr))
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(18.5, 10.5)
        print("saving to {}".format(utils.output_rel_path(asset+".png")))
        fig.savefig(utils.output_rel_path(asset+".png"), dpi=100)

    def stack_plot(self):
        pass

    def bar_plot(self):
        pass

    def pie_plot(self):
        pass

    def generate_plot(self):
        # Using Plotly to generate plots
        if self.plot_type == "TIME SERIES":
            self.timeseries_plot()
        elif self.plot_type == "BAR":
            self.bar_plot()
        elif self.plot_type == "PIE":
            self.pie_plot()
        elif self.plot_type == "STACK":
            self.stack_plot()
        else:
            return "PLOT_TYPE Error"
