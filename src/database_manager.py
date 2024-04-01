import sqlite3
import pandas as pd
from loguru import logger


DEFAULT_DATABASE_PATH = "data/database.db"


class DatabaseManager:
    def __init__(self, db_name: str = DEFAULT_DATABASE_PATH):
        self.db_name: str = db_name

        self.table_names = {
            "cluster_descriptions": "clusters",
            "comments_analytics": "comments_analysis",
            "comments": "geo_comments"
        }

    def save_to_analysis_table(self, id_to_cluster: dict[int, int], id_to_sentiment: dict[int, str]):
        assert set(id_to_sentiment.keys()) == set(id_to_cluster.keys())
        indexes = set(id_to_sentiment.keys())

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                for idx in indexes:
                    sql_query = (f'INSERT INTO {self.table_names["comments_analytics"]} '
                                 f'(id, cluster_id, sentiment) VALUES (?, ?, ?)')
                    sentiment = id_to_sentiment[idx]
                    cluster_id = id_to_cluster[idx]

                    cursor.execute(sql_query, (idx, cluster_id, sentiment))
                conn.commit()
        except Exception as e:
            logger.error(f"An error occurred while saving sentiment data: {repr(e)}")

    def save_to_clusters_table(self, cluster_descriptions: pd.DataFrame):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cluster_descriptions.to_sql("clusters", conn, if_exists="append", index=False)
        except Exception as e:
            logger.error(f"An error occurred while saving clusters data: {repr(e)}")

    def is_cached(self, company_name: str) -> bool:
        """Check whether clusters were already calculated for given company name"""
        query = f'SELECT COUNT(*) from {self.table_names["cluster_descriptions"]}  WHERE name == "{company_name}";'

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                num_rows = int(cursor.fetchone()[0])
        except Exception as e:
            logger.error(f"An error occurred while checking for cached result: {repr(e)}")

        logger.info(f'Found {num_rows} rows for {company_name} in {self.table_names["cluster_descriptions"]} table.')
        logger.info(f"is_cached: {num_rows != 0}")

        return num_rows != 0

    def get_data_for_analytics(self, company_name: str) -> pd.DataFrame:
        """Collect data for analysis"""
        # TODO execute query for getting data
        # Тут select запросы в том формате, который потом требуется для visualizer.py

        return None

    def get_company_data(self, company_name: str) -> pd.DataFrame:
        """Collect data for analysis"""
        query = f'SELECT * FROM {self.table_names["comments"]} WHERE name = "{company_name}";'
        logger.info(f"SQL query for getting infi about company: {query}")

        try:
            with sqlite3.connect(self.db_name) as conn:
                company_data = pd.read_sql_query(query, conn)

                logger.info(f"Collected data from database for company: {company_name}")
        except Exception as e:
            logger.error(f"An error occurred while collecting data: {repr(e)}")
            company_data = pd.DataFrame()

        return company_data
