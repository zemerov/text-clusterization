from bertopic import BERTopic
from loguru import logger

DEFAULT_ENCODER_PATH = "distiluse-base-multilingual-cased-v1"


class Clusterizer:
    def __init__(
        self, encoder_path: str = DEFAULT_ENCODER_PATH, min_topic_size: int = 10
    ):
        self.topic_model = BERTopic(
            embedding_model=encoder_path,
            verbose=True,
            min_topic_size=min_topic_size,
            calculate_probabilities=True,
        )

        logger.info(f"Created topic model: {self.topic_model}")

    def predict_topics(self, texts: list[str]) -> (list[int], dict[int, str], dict[str, int]):
        logger.info(f"Predicting topics for {len(texts)} texts...")
        topics, _ = self.topic_model.fit_transform(texts)
        logger.info(f"Predicted distinct topics: {len(set(topics))}")

        topic_info = self.topic_model.get_topic_info()[["Topic", "Name"]]
        topic_info.columns = ["topics", "keywords"]
        topic_info["keywords"] = topic_info["keywords"].apply(
            lambda x: ", ".join(x.split("_")[1:])
        )

        topic_info = {
            topic_id: keywords
            for topic_id, keywords in zip(topic_info["topics"], topic_info["keywords"])
        }

        # Создание словаря для привязки текстов к кластерам
        text_cluster_mapping = {text: topic for text, topic in zip(texts, topics)}

        return topics, topic_info, text_cluster_mapping

