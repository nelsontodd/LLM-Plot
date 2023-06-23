export PROJECT_DIR=$(pwd)
export ABS_SRC_DIR=$(realpath "src/")
export OPENAI_API_KEY=""
export OPENAI_USER=""
export OPENAI_MODEL="gpt-3.5-turbo"
export PYTHONPATH="$PYTHONPATH:$ABS_SRC_DIR"
export TWITTER_ACCESS_TOKEN=""
export TWITTER_ACCESS_TOKEN_SECRET=""
export TWITTER_BEARER_TOKEN=""
export TWITTER_API_KEY=""
export TWITTER_API_KEY_SECRET=""
export COINGECKO_API=""
export ETHERSCAN_API_KEY=""
echo "PROJECT_DIR = "$PROJECT_DIR
export ARKHAM_API_KEY=""

export TWITTER_CLIENT_ID=""
export TWITTER_CLIENT_ID_SECRET=""
#if [ ! -d ".venv/bin" ]; then
if [$VIRTUAL_ENV == ""]; then
  echo ".venv does not exist."
  virtualenv .venv
  source .venv/bin/activate
  pip3 install -r requirements.txt
fi
pip3 install -r requirements.txt
