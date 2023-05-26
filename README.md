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

`import langpipeline`

- Instantiate the walletviz object with a prompt  
`wallet = langpipeline.walletviz("Plot the price of bitcoin over the last 30 days.")`

- Generate the plot  
`wallet.generate_plot()`

## TODO

1. **Scalability via Celery and RabbitMQ**: On deployment, this is main priority.

2. **Transition to Plotly from Matplotlib**: Plotly can generate plots from JSON dictionaries. This would make going from input to plot relatively seamless.The difficulty is to *reliably* train an LLM to generate dictionaries for Plotly. Unit tests will ensure effective LLM training. The ~4k token context window offered by GPT-3.5-turbo should be more than enough to do this.

3. **Establishment of a User Dashboard**: At a static URL, give users a default dashboard. Possibly include a chatbot for basic plot input.

4. **Storage of Basic Plots on Disk** : Could save compute and decrease response time.

5. **Introduction of a View Mode for Wallet Addresses**: A 'view mode' is being explored, enabling the connection of a wallet address without requiring a private key.

6. **Implement etherscan/blockchain.info/bscscan api**: This will allow us to extract
   information on user holdings. 

