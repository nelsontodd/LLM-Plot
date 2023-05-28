# LLM-Plot

This repository contains code for plotting cryptocurrency wallet data using the `walletviz` library.

## Install

```bash
# Clone the repository
git clone https://github.com/nelsontodd/llm-plot

# Create a virtual environment
virtualenv .venv

# Copy the environment template file
cp env_template.sh env.sh

# Replace the placeholder values in env.sh with your API keys

# Install the required dependencies
pip3 install -r requirements.txt
```
## Example Usage

- Import
- `import langplot`

- Instantiate the langplot factory object with a prompt
- `factory = langplot.PlotterFactory("Plot the price of bitcoin and the volume of eth over the last week")`

- Generate the plot
- `plotter = factory.create_plotter()`
- `plotter.plot(theme='plotly_dark')`

## TODO

1. **Scalability via Celery and RabbitMQ**: On deployment, this is main priority.

2. **Establishment of a User Dashboard**: At a static URL, give users a default dashboard. Possibly include a chatbot for basic plot input.

3. **Storage of Basic Plots on Disk** : Could save compute and decrease response time.

4. **Introduction of a View Mode for Wallet Addresses**: A 'view mode' is being explored, enabling the connection of a wallet address without requiring a private key.

5. **Implement etherscan/blockchain.info/bscscan api**: This will allow us to extract
   information on user holdings. 

