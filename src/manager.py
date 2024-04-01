import pandas as pd

from sentiment_classifier import SentimentClassifier
from clusterizer import Clusterizer
from openai_api_wrapper import OpenAIAPIWrapper
from database_manager import DatabaseManager, DEFAULT_DATABASE_PATH

from pathlib import Path


class Manager:
    def __init__(self, db_path: str = DEFAULT_DATABASE_PATH):
        self.sentiment_classifier = SentimentClassifier()
        self.clusterizer = Clusterizer()
        self.api_wrapper = OpenAIAPIWrapper()

        self.db_manager = DatabaseManager(db_name=db_path)

    def get_report(self, company_name: str):
        if not self.db_manager.is_cached(company_name):
            company_comments: pd.DataFrame = self.db_manager.get_company_data(company_name)

            # Calculate and save sentiments
            sentiments, _ = self._get_sentiment(company_comments)
            cluster_ids, cluster_descriptions = self._get_clusters(company_comments, company_name)

            id_to_sentiment = {idx: sentiment for idx, sentiment in zip(company_comments["id"], sentiments)}
            id_to_cluster = {idx: cluster_id for idx, cluster_id in zip(company_comments["id"], cluster_ids)}

            self.db_manager.save_to_analysis_table(id_to_cluster, id_to_sentiment)
            self.db_manager.save_to_clusters_table(cluster_descriptions)

        result = self._get_analytics(company_name)

        return result

    def _get_clusters(self, comments: pd.DataFrame, company_name: str) -> (list[int], pd.DataFrame):
        topics, topics_info, _ = self.clusterizer.predict_topics(comments["text"].tolist())
        comments["topics"] = topics

        cluster_descriptions = []
        for cluster_id in set(topics):
            cluster_comments = comments[comments["topics"] == cluster_id]["text"].tolist()
            cluster_summary = self.api_wrapper.get_cluster_summary(
                cluster_comments, topics_info[cluster_id]
            )
            cluster_descriptions.append(
                {
                    "name": company_name,
                    "cluster_id": cluster_id,
                    "keywords": topics_info[cluster_id],
                    "description": cluster_summary
                }
            )

        return topics, pd.DataFrame(cluster_descriptions)

    def _get_sentiment(self, company_comments: pd.DataFrame) -> (list[str], dict[str: list[float]]):
        texts = company_comments["text"].tolist()
        all_sentiments, scores = self.sentiment_classifier.predict_sentiment(texts)

        return all_sentiments, scores

    def _get_analytics(self, company_name: str) -> list[Path]:
        """
        Create analytics plots, save them to files and return paths to these files

        :param company_name: str name for the company to create analytics
        :return: list of paths to images and tables
        """
        data = self.db_manager.get_data_for_analytics(company_name)

        # TODO place logic for plots creation

        resulting_file_paths = [
            # TODO replace with actual paths for files
            Path('resources/example/planet_comments.csv'),
            Path('resources/example/top_categories_plot.png')
        ]

        return resulting_file_paths


if __name__ == "__main__":
    # Only for debugging
    name = "Мираторг"

    manager = Manager()
    manager.get_report(company_name=name)
