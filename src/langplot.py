import json
import utils
import constants
import coingecko_api
from datetime import timedelta
from datetime import datetime
import random
import plotly.graph_objects as go
import plotly.io as pio

class LangPlot:
    def __init__(self, prompt, instructions, theme='ggplot2', model="gpt-3.5-turbo"):
        self.prompt = prompt
        self.instructions = instructions
        self.model=model
        pio.templates.default = theme
        self.plot_type = self.instructions['PLOT_TYPE']
        self.plot_duration = self.instructions['PLOT_DURATION']
        self.were_dates_specified = self.instructions['SPECIFIC_DATES_SPECIFIED']
        self.plot_dates = self.instructions['PLOT_DATES']
        self.assets = self.instructions['ASSETS']
        self.required_asset_data = self.instructions['REQUIRED_ASSET_DATA']
        self.user_owns_asset = self.instructions['USER_OWNS_ASSET']

    def plot(self):
        raise NotImplementedError("Please Implement this method in subclass")

class BarPlot(LangPlot):
    pass

class PiePlot(LangPlot):
    pass

class TimeSeriesPlot(LangPlot):

    def __init__(self, prompt,instructions, theme='ggplot2', model="gpt-3.5-turbo"):
        super().__init__(prompt,instructions, theme=theme, model=model)
        self.systemprompt = constants.TIMESERIES_PLOTLY_SPEC
        rawtext = utils.promptGPT(self.systemprompt, prompt, self.model)
        with open("raw.json", "w") as f:
            f.write(rawtext)
        plotly_spec = json.loads(rawtext)
        self.plot_data   = plotly_spec['data']
        self.plot_layout = plotly_spec['layout']

    def fetch_data(self):
        if self.user_owns_asset == True:
            self.get_wallet_data = self.get_coingecko_data
            return self.get_wallet_data()
        elif self.user_owns_asset == False:
            return self.get_coingecko_data()
        else:
            return "USER_OWNS_ASSET Ambiguous"

    def get_coingecko_data(self):
        #data_points = {}
        data_list = []
        def get_asset_data_from_coingecko(asset, data):
            if data == "PRICE":
                return coingecko_api.handle_ts_json(coingecko_api.historical_market_data(asset,
                    days=str(self.plot_duration.days)), market_data_type="prices")
            if data == "VOLUME":
                return coingecko_api.handle_ts_json(coingecko_api.historical_market_data(asset,
                    days=str(self.plot_duration.days)), market_data_type="total_volumes")
            if data == "MARKETCAP":
                return coingecko_api.handle_ts_json(coingecko_api.historical_market_data(asset,
                    days=str(self.plot_duration.days)), market_data_type="market_caps")
        for asset in self.assets:
            #data_points[asset] = {}
            for data in self.required_asset_data[asset]:
                #data_points[asset][data] = get_asset_data_from_coingecko(asset, data)
                data_list.append(get_asset_data_from_coingecko(asset, data.upper()))
        print(data_list)
        return data_list#data_points

    def plot(self):
        # Using Plotly to generate plots
        asset_data = self.fetch_data()
        #for index,asset in enumerate(asset_data.keys()):
            #df = asset_data[asset]["PRICE"]
            #self.plot_data[index]["x"] = df['timestamp']
            #self.plot_data[index]["y"] = df['value']
        for index, df in enumerate(asset_data):
            self.plot_data[index]["x"] = df['timestamp']
            self.plot_data[index]["y"] = df['value']

        fig = go.Figure(data=self.plot_data, layout=self.plot_layout)
        pio.write_image(fig,
                utils.output_rel_path('{}.png'.format("INSERT_USER_NAME_")))
        return 0


class PlotterFactory:

    def __init__(self, prompt, model="gpt-3.5-turbo"):
        self.initprompt = prompt
        self.model=model
        ##Prompt #1 of 2: ~350 tokens
        rawtext = utils.promptGPT(constants.INSTRUCTIONS_JSON,
            prompt, self.model)
        raw = json.loads(rawtext)
        instructions_json = self.reformat(raw)
        instructions_json['ASSETS'] = list(map(lambda x: coingecko_api.match_coin_id(x),
            instructions_json['ASSETS']))
        def fuzzymatch_keys(original_dict):
            return {coingecko_api.match_coin_id(k): v for k, v in original_dict.items()}

        instructions_json['REQUIRED_ASSET_DATA'] = fuzzymatch_keys(instructions_json['REQUIRED_ASSET_DATA'])
        self.instructions = instructions_json

    @staticmethod
    def reformat(instructions_json):
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

    def create_plotter(self, theme='ggplot2'):
        plot_classes = {'BAR': BarPlot, 'PIE': PiePlot, 'TIME SERIES': TimeSeriesPlot}
        
        if self.instructions['PLOT_TYPE'] in plot_classes:
            return plot_classes[self.instructions['PLOT_TYPE']](self.initprompt, self.instructions, theme=theme, model=self.model)
        else:
            raise ValueError("""Error: ambiguous plot definition. Could not determine plot
            type.""")
