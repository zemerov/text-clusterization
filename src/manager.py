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
            # TODO load data from database
            company_comments: pd.DataFrame = self.loader.get_company_comments(company_name)

            sentiments: pd.DataFrame = self._get_sentiment(company_comments)
            clusters: pd.DataFrame = self._get_clusters(company_comments)

            self.db_manager.save_sentiment(sentiments)
            self.db_manager.save_clusters(clusters)

        result = self._get_analytics(company_name)

        return result

    def _get_clusters(self, comments: pd.DataFrame) -> pd.DataFrame:
        
        topics, topics_info = self.clusterizer.predict_topics(comments["text"].tolist())
        cluster_df = pd.DataFrame(columns=["cluster_id", "keywords", "description"])
        for cluster_id in set(topics):
            cluster_comments = comments[comments["topics"] == cluster_id]["text"].tolist()
            cluster_summary = self.api_wrapper.get_cluster_summary(
                cluster_comments, topics_info[cluster_id]
            )
            cluster_df = cluster_df.append({
                "cluster_id": cluster_id,
                "keywords": topics_info[cluster_id],
                "description": cluster_summary
            }, ignore_index=True)

        return cluster_df

    def _get_sentiment(self, company_comments: pd.DataFrame) -> pd.DataFrame:
        texts = company_comments["text"].tolist()
        all_sentiments, _ = self.sentiment_classifier.predict_sentiment(texts)

        return all_sentiments

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
