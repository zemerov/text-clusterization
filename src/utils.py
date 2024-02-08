import pandas as pd
import json
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes


class Dumper:
    def __init__(self, file_name='data/log.jsonl'):
        self.file = open(file_name, 'a')
        self.file_name = file_name

    def dump(self, *args, **kwargs):
        if len(args) > 0:
            logger.warning(f"You are trying to dump values without attribute names: {args}; "
                           f"Please pass arguments in format: .dump(key_1=value_1, key_2=value_2, ...)")

        logger.info(f"Dump to {self.file_name}: {kwargs}")

        print(json.dumps(kwargs, ensure_ascii=False), file=self.file, flush=True)

    def __del__(self):
        self.file.close()


def log_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"Got message {update.message.text} from {user['username']} with id {user['id']}")


def load_phrases(path: str = "resources/phrases.json") -> dict[str, str]:
    with open(path, "r") as file:
        phrases = json.load(file)

    return phrases
