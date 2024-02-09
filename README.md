# Text clusterization for Yandex.Maps reviews

**Master thesis project for MiBA GSOM `24.**

## How to run Telegram bot

Install requirements

```pip install -r requirements.txt```

Make sure the dataset file is stores in `./data/` directory

Setup OPEN_AI_KEY

```export OPEN_AI_KEY=sk-...```

Setup BOT_TOKENTelegram API key

```export BOT_TOKEN=...```

Run telegram bot with default parameters

```python src/bot.py```

## Repository structure

`src/` — directory with source code

`notebooks/` — directory for notebooks

`data/` — data directory

`resources/` — directory for json, yaml, images etc.

## Citation

Original dataset [here](https://github.com/yandex/geo-reviews-dataset-2023)
