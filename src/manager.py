import pandas as pd

from loader import Loader
from sentiment_classifier import SentimentClassifier
from clusterizer import Clusterizer
from openai_api_wrapper import OpenAIAPIWrapper
from database_manager import DatabaseManager


class Manager:
    def __init__(self, source_path: str):
        self.loader = Loader(source_path)
        self.sentiment_classifier = SentimentClassifier()
        self.clusterizer = Clusterizer()
        self.api_wrapper = OpenAIAPIWrapper()

        self.db_manager = DatabaseManager()

    def get_report(self, company_name: str):
        if not self.db_manager.is_cached(company_name):
            # Company does not have clusterization yet.
            company_comments: pd.DataFrame = self.loader.get_company_comments(company_name)

            self._get_sentiment(company_comments["text"].tolist())
            self._get_clusters(company_comments)

        result = self._get_analytics(company_name)

        return result

    def _get_clusters(self, comments: pd.DataFrame):
        topics, topics_info = self.clusterizer.predict_topics(comments["text"].tolist())

        comments["topics"] = topics

        cluster_summaries: list[str] = self.api_wrapper.get_cluster_summaries(
            topics, comments, topics_info
        )

        self.db_manager.save_clusters()

    def _get_sentiment(self, texts: list[str]):
        all_sentiments, _ = self.sentiment_classifier.predict_sentiment(texts)

        self.db_manager.save_sentiment(all_sentiments)

    def _get_analytics(self, company_name: str):
        data = self.db_manager.get_data_for_analytics(company_name)

        # Create analytics based on data
        # Save analytics (MAYBE)
        # Return smth
        return 2 + 2


if __name__ == "__main__":
    # Only for debugging
    table_path = "data/geo-reviews-dataset-2023-full.jsonl"
    name = "INVITRO"

    manager = Manager(table_path)
    manager.get_report(company_name=name)
