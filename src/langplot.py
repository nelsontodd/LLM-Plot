import json
import utils
import constants
import coingecko_api
from datetime import timedelta
from datetime import datetime
import random
import plotly.graph_objects as go
import plotly.io as pio
import arkham_api
import webdrive

class LangPlot:
    def __init__(self, prompt, instructions, model="gpt-3.5-turbo", address=None):
        self.prompt = prompt
        self.instructions = instructions
        self.model=model
        if address:
            self.address = address
        self.plot_type = self.instructions['PLOT_TYPE']
        self.plot_duration = self.instructions['PLOT_DURATION']
        self.were_dates_specified = self.instructions['SPECIFIC_DATES_SPECIFIED']
        self.plot_dates = self.instructions['PLOT_DATES']
        self.assets = self.instructions['ASSETS']
        self.required_asset_data = self.instructions['REQUIRED_ASSET_DATA']
        self.user_owned = self.instructions['USER_OWNED']

    def plot(self):
        raise NotImplementedError("Please Implement this method in subclass")

class BarPlot(LangPlot):
    pass

class PiePlot(LangPlot):
    def __init__(self, prompt,instructions, model="gpt-3.5-turbo", address=None):
        super().__init__(prompt,instructions, model=model, address=address)
        self.systemprompt = constants.PIE_PLOTLY_SPEC
        rawtext = utils.promptGPT(self.systemprompt, prompt, self.model)
        with open("raw.json", "w") as f:
            f.write(rawtext)
        plotly_spec = json.loads(rawtext)
        self.plot_data   = plotly_spec['data']
        self.plot_layout = plotly_spec['layout']
    def plot(self, theme="plotly_dark"):
        pio.templates.default = theme
        def remove_empty_values(my_dict):
            return {k: v for k, v in my_dict.items() if v}
        wallet = remove_empty_values(arkham_api.get_portfolio_endpoint(self.address))
        labels = []
        values = []
        for chain in wallet:
            for asset in wallet[chain]:
                labels.append(asset)
                values.append(wallet[chain][asset]['usd'])
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)],
                layout=self.plot_layout)
        pio.write_image(fig,
                utils.output_rel_path('{}.png'.format("INSERT_USER_NAME_")))

class TimeSeriesPlot(LangPlot):

    def __init__(self, prompt,instructions, model="gpt-3.5-turbo", address=None):
        super().__init__(prompt,instructions, model=model, address=address)
        self.systemprompt = constants.TIMESERIES_PLOTLY_SPEC
        rawtext = utils.promptGPT(self.systemprompt, prompt, self.model)
        with open("raw.json", "w") as f:
            f.write(rawtext)
        plotly_spec = json.loads(rawtext)
        self.plot_data   = plotly_spec['data']
        self.plot_layout = plotly_spec['layout']

    def fetch_data(self):
        internal = self.get_wallet_data()
        external = self.get_coingecko_data()
        return (internal, external)

    def get_wallet_data(self):
        #Only thing I can do time series wise right now is return balance of the whole
        #thing.
        #Good news: it works for arbitrary chains, including bitcoin, arbitrum, bsc, etc
        if "WHOLE PORTFOLIO" in self.assets:
            return arkham_api.historical_balance(self.address)
        for asset in self.assets:
            if 'VALUE' in self.required_asset_data[asset]: #Bandaid
                return arkham_api.historical_balance(self.address, chain=asset)
        return None
    def get_coingecko_data(self):
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
            for data in self.required_asset_data[asset]:
                if self.user_owned[asset]['USER_OWNED'] == False:
                    data_list.append(get_asset_data_from_coingecko(asset, data.upper()))
        return data_list

    def plot(self, theme="plotly_dark"):
        # Using Plotly to generate plots
        pio.templates.default = theme
        (wallet, coingecko) = self.fetch_data()
        #for index,asset in enumerate(asset_data.keys()):
            #df = asset_data[asset]["PRICE"]
            #self.plot_data[index]["x"] = df['timestamp']
            #self.plot_data[index]["y"] = df['value']
        def wallet_trace_first():
            if ('Value' in self.plot_data[0]['name']) or ('Portfolio' in self.plot_data[0]['name']) or ('Worth' in self.plot_data[0]['name']):
                return True
            else:
                return False
        if wallet_trace_first():
            df = wallet.tail(int(self.plot_duration.days))
            self.plot_data[index]["x"] = df.index
            self.plot_data[index]["y"] = df['value']

            for index, df in enumerate(coingecko):
                self.plot_data[1+index]["x"] = df.index
                self.plot_data[1+index]["y"] = df['value']
        else:
            num_external = 0
            for index, df in enumerate(coingecko):
                self.plot_data[index]["x"] = df.index
                self.plot_data[index]["y"] = df['value']
                num_external +=1
            df = wallet.tail(int(self.plot_duration.days))
            print(num_external)
            self.plot_data[num_external]["x"] = df.index
            self.plot_data[num_external]["y"] = df['value']
        self.plot_layout['yaxis'].update({'showgrid':False})
        self.plot_layout['xaxis'].update({'showgrid':False})
        if 'yaxis2' in self.plot_layout.keys():
            self.plot_layout['yaxis2'].update({'showgrid':False})
        fig = go.Figure(data=self.plot_data, layout=self.plot_layout)
        pio.write_image(fig,
                utils.output_rel_path('{}.png'.format("INSERT_USER_NAME_")))
        return 0


class PlotterFactory:

    def __init__(self, prompt, model="gpt-3.5-turbo", user_address="0x5a68c82e4355968db53177033ad3edcfd62accca"):
        self.initprompt = prompt
        self.model=model
        self.address = user_address

        ##Prompt #1 of 2: ~350 tokens
        rawtext = utils.promptGPT(constants.INSTRUCTIONS_JSON,
            prompt, self.model)
        with open("raw.json", "w") as f:
            f.write(rawtext)
        raw = json.loads(rawtext)
        instructions_json = self.reformat(raw)
        def fuzzymatch_keys(original_dict):
            return {coingecko_api.match_coin_id(k): v for k, v in original_dict.items()}
        instructions_json['ASSETS'] = list(map(lambda x: coingecko_api.match_coin_id(x), instructions_json['ASSETS']))
        instructions_json['REQUIRED_ASSET_DATA'] = fuzzymatch_keys(instructions_json['REQUIRED_ASSET_DATA'])
        instructions_json['USER_OWNED'] = fuzzymatch_keys(instructions_json['USER_OWNED'])
        self.instructions = instructions_json

    @staticmethod
    def reformat(instructions_json):
        if type(instructions_json['PLOT_DURATION']) == str:
            instructions_json['PLOT_DURATION'] = eval(instructions_json['PLOT_DURATION']) #Security risk
        if type(instructions_json['REQUIRED_ASSET_DATA']) == str:
            instructions_json['REQUIRED_ASSET_DATA'] = [instructions_json['REQUIRED_ASSET_DATA']]
        if type(instructions_json['SPECIFIC_DATES_SPECIFIED']) == str:
            instructions_json['SPECIFIC_DATES_SPECIFIED'] = eval(instructions_json['SPECIFIC_DATES_SPECIFIED'])

        if type(instructions_json['ASSETS']) == str:
            instructions_json['ASSETS'] = [instructions_json['ASSETS']]
        if 'ether' in list(map(lambda x: x.lower(), instructions_json['ASSETS'])):
            instructions_json['ASSETS'][list(map(lambda x: x.lower(), instructions_json['ASSETS'])).index('ether')] = 'ETH'

        if 'ether' in instructions_json['REQUIRED_ASSET_DATA'].keys():
            instructions_json['REQUIRED_ASSET_DATA']['ETH'] = my_dict.pop('ether')
        if 'Ether' in instructions_json['REQUIRED_ASSET_DATA'].keys():
            instructions_json['REQUIRED_ASSET_DATA']['ETH'] = my_dict.pop('Ether')
        if 'ETHER' in instructions_json['REQUIRED_ASSET_DATA'].keys():
            instructions_json['REQUIRED_ASSET_DATA']['ETH'] = my_dict.pop('ETHER')

        if 'ether' in instructions_json['USER_OWNED'].keys():
            instructions_json['USER_OWNED']['ETH'] = my_dict.pop('ether')
        if 'Ether' in instructions_json['USER_OWNED'].keys():
            instructions_json['USER_OWNED']['ETH'] = my_dict.pop('Ether')
        if 'ETHER' in instructions_json['USER_OWNED'].keys():
            instructions_json['USER_OWNED']['ETH'] = my_dict.pop('ETHER')
        return instructions_json

    def create_plotter(self):
        plot_classes = {'BAR': BarPlot, 'PIE': PiePlot, 'TIME SERIES': TimeSeriesPlot}
        
        if self.instructions['PLOT_TYPE'] in plot_classes:
            return plot_classes[self.instructions['PLOT_TYPE']](self.initprompt,
                    self.instructions, model=self.model, address=self.address)
        else:
            raise ValueError("""Error: ambiguous plot definition. Could not determine plot
            type.""")
