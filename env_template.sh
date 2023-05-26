export PROJECT_DIR=$(pwd)
export ABS_SRC_DIR=$(realpath "src/")
export OPENAI_API_KEY=""
export OPENAI_USER=""
export OPENAI_MODEL="gpt-3.5-turbo"
export PYTHONPATH="$PYTHONPATH:$ABS_SRC_DIR"
export COINGECKO_API=""
source .venv/bin/activate
echo "PROJECT_DIR = "$PROJECT_DIR
