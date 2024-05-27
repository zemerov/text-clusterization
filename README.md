# Text clusterization for Yandex.Maps reviews

**Master thesis project for MiBA GSOM `24.**

## How to setup envieronment

Install requirements:

```pip install -r requirements.txt```

Make sure the dataset file is stores in `./data/` directory

Setup OPEN_AI_KEY:

```export OPEN_AI_KEY=sk-...```

Create and load comments to the database. Make sure you have the json file with 
the data storing with this path `"data/geo-reviews-dataset-2023-full.jsonl"`:

```python src/create_database.py```

Run example script:
```python src/manager.py```

Setup BOT_TOKENTelegram API key (If you want to run TG bot):

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
