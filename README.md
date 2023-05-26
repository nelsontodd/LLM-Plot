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

