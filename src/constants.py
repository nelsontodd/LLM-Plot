import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")
username=os.getenv("OPENAI_USER")
output_path = os.getenv("PROJECT_DIR")+"/outputs/"
data_path = os.getenv("PROJECT_DIR")+"/market-data/"
os.makedirs(output_path, exist_ok=True)
os.makedirs(data_path, exist_ok=True)

INSTRUCTIONS_JSON = """
You are part of the data pipeline that takes user prompt and turns it into data
visualization, like a chart of some kind. From the user input below, fill in the values in
the following JSON. Respond with ONLY the filled JSON output. QTY_HELD is necessary asset
data to determine portfolio value. if there are multiple REQUIRED_ASSET_DATA, format them as
python list. If the user uses the word "my" - it means they are referring to assets they
own.
{
            "PLOT_TYPE": "BAR OR PIE OR TIME SERIES OR STACK",
            "PLOT_DURATION": "False OR timedelta(days=0)",
            "SPECIFIC_DATES_SPECIFIED": "True OR False",
            "PLOT_DATES": "%m-%d-%y",
            "REQUIRED_ASSET_DATA": "PRICE ANDOR MARKETCAP ANDOR QTY HELD ANDOR TOKEN SUPPLY",
            "ASSETS": "ALL_OWNED OR ASSET_PYTHON_LIST",
            "USER_OWNS_ASSET": "True OR False"
        }
"""
