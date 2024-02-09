from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
)
import torch
from loguru import logger
from tqdm.auto import tqdm

DEFAULT_SENTIMENT_CLASSIFIER = "Tatyana/rubert-base-cased-sentiment-new"


class SentimentClassifier:
    ID_TO_SENTIMENT = {
        0: "NEUTRAL",
        1: "POSITIVE",
        2: "NEGATIVE",
    }

    SENTIMENT_TO_ID = {v: k for k, v in ID_TO_SENTIMENT.items()}

    def __init__(
        self,
        model_name: str = DEFAULT_SENTIMENT_CLASSIFIER,
        batch_size: int = 32,
        device: torch.device | str = "cpu",
    ):
        self.model: PreTrainedModel = (
            AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
        )
        self.tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(model_name)

        self.batch_size: int = batch_size
        self.device: torch.device | str = device

        logger.info(
            f"Loaded sentiment classifier: {model_name}. Batch size: {batch_size}. Device: {device}"
        )

    @torch.inference_mode
    def predict_sentiment(self, texts: list[str]) -> tuple[list[str], list[float]]:
        sentiments = []
        negative_scores = []

        for i in tqdm(
            range(0, len(texts), self.batch_size), desc="Calculating sentiment scores"
        ):
            texts_batch = texts[i : i + self.batch_size]

            tokenized_batch = {
                k: v.to(self.device)
                for k, v in self.tokenizer(
                    texts_batch,
                    return_tensors="pt",
                    padding="longest",
                    truncation=True,
                    max_length=512,
                ).items()
            }

            predictions = self.model(**tokenized_batch).logits
            negative_scores.append(predictions[:, self.SENTIMENT_TO_ID["NEGATIVE"]])
            sentiments.append(predictions.argmax(dim=1))

        negative_scores = torch.cat(negative_scores).tolist()
        sentiments = torch.cat(sentiments).tolist()
        sentiments = [self.ID_TO_SENTIMENT[x] for x in sentiments]

        return sentiments, negative_scores
