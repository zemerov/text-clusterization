from loader import Loader
from sentiment_classifier import SentimentClassifier
from clusterizer import Clusterizer
from openai_api_wrapper import OpenAIAPIWrapper

from tqdm.auto import tqdm


class Manager:
    def __init__(self, source_path: str):
        self.loader = Loader(source_path)
        self.sentiment_classifier = SentimentClassifier()
        self.clusterizer = Clusterizer()
        self.api_wrapper = OpenAIAPIWrapper()

    def get_report(self, rubric: str, company_name: str):
        # TODO check for cached result in database
        all_comments = self.loader.get_data(rubric, company_name)
        company_comments = all_comments[all_comments["name_ru"] == company_name]

        all_sentiments = self.sentiment_classifier.predict_sentiment(
            all_comments["text"].tolist()
        )
        topics, topics_info = self.clusterizer.predict_topics(
            company_comments["text"].tolist()
        )

        company_comments["topics"] = topics

        cluster_summaries = []

        for cluster_id in tqdm(
            range(len(set(topics)) - 1), desc="Generating cluster summaries"
        ):
            cluster_comments = company_comments[
                company_comments["topics"] == cluster_id
            ]["text"].tolist()
            cluster_summaries.append(
                self.api_wrapper.get_cluster_summary(
                    cluster_comments, topics_info[cluster_id]
                )
            )

        result = {}  # TODO define result
