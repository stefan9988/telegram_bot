# Telegram Bot

This project comprises several Python scripts that send daily updates to Telegram chats. It gathers cryptocurrency data, inspirational quotes, and business psychology insights, delivering them through the Telegram Bot API.

## Setup

### Prerequisites
- Python 3.12
- [Poetry](https://python-poetry.org/) for dependency management

### Installation

```bash
git clone https://github.com/stefan9988/telegram_bot.git
cd telegram_bot
poetry install
```

### Environment variables

Create a `.env` file in the project root with the required credentials:

```dotenv
BTC_BOT_TOKEN=<telegram bot token for crypto updates>
QOTD_BOT_TOKEN=<telegram bot token for quote of the day>
BUSINESS_BOT_TOKEN=<telegram bot token for business psychology updates>
TELEGRAM_USER_ID=<your telegram user id>

# LLM credentials
AZURE_OPENAI_API_KEY=<azure key>       # used when LLM_PROVIDER is AZURE
AZURE_OPENAI_ENDPOINT=<azure endpoint> # used when LLM_PROVIDER is AZURE
OPEN_ROUTER_API_KEY=<openrouter key>   # used when LLM_PROVIDER is OPEN_ROUTER
```

### Data directory

Scripts output CSV files and images to `data/`. Create it if it doesn't exist:

```bash
mkdir -p data
```

### Running the scripts

Each script can be run individually depending on which bot you want to update.

```bash
poetry run python fetch_all_data.py
poetry run python crypto_main.py
poetry run python quote_of_the_day.py
poetry run python business_psychology.py
```

### Tests

Run the test suite to verify the installation:

```bash
PYTHONPATH=. poetry run pytest
```

## Git Hooks

To ensure the test suite runs before code is pushed, configure Git to use the hooks in this repository:

```bash
git config core.hooksPath .githooks
```

The included `pre-push` hook runs `PYTHONPATH=. pytest` and prevents the push if any tests fail.

## Cron Jobs

Schedule the scripts with cron to send updates automatically by adding these lines to crontab (`crontab -e`):

```
# m h  dom mon dow   command
20 8  * * * cd /path/to/telegram_bot && PYTHONPATH=. poetry run python fetch_all_data.py      >> /path/to/telegram_bot/cron.log 2>&1
25 8  * * * cd /path/to/telegram_bot && PYTHONPATH=. poetry run python crypto_main.py         >> /path/to/telegram_bot/cron.log 2>&1
20 20 * * * cd /path/to/telegram_bot && PYTHONPATH=. poetry run python quote_of_the_day.py    >> /path/to/telegram_bot/cron.log 2>&1
2 20 * * * cd /path/to/telegram_bot && PYTHONPATH=. poetry run python business_psychology.py >> /path/to/telegram_bot/cron.log 2>&1
```

## License
[MIT](LICENSE)
