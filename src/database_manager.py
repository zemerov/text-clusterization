import sqlite3
import pandas as pd
import json
from loguru import logger


DEFAULT_DATABASE_PATH = "data/database.db"


class DatabaseManager:
    def __init__(self, db_name: str = DEFAULT_DATABASE_PATH, queries_file: str = "resources/queries.json"):
        self.db_name: str = db_name

        with open(queries_file, "r") as file:
            self.queries: dict[str, str] = json.load(file)

    def save_clusters(self, df_clusters: pd.DataFrame, table_name: str, text_table_name: str, text_column_name: str):
        # Сохраняет информацию о кластерах в базу данных и добавляет cluster_id к текстам в другой таблице
        try:
            with sqlite3.connect(self.db_name) as conn:
                # Сохраняем информацию о кластерах в отдельную таблицу
                df_clusters.to_sql(table_name, conn, if_exists="append", index=False)
                logger.info(f"Clusters data saved to table {table_name} in the database.")

                # Добавляем cluster_id к текстам в другой таблице
                cursor = conn.cursor()
                for index, row in df_clusters.iterrows():
                    cluster_id = row["cluster_id"]
                    # Используем SQL-запрос для добавления cluster_id к текстам в таблице geo_comments_data
                    sql_query = f"UPDATE {text_table_name} SET cluster_id = ? WHERE cluster_id IS NULL AND {text_column_name} = ?"
                    cursor.execute(sql_query, (cluster_id, row["text"]))
                conn.commit()
                logger.info(f"Cluster IDs added to table {text_table_name} in the database.")
        except Exception as e:
            logger.error(f"An error occurred while saving clusters data: {e}")

    def save_sentiment(self, sentiments: list[str]):
        pass

    def is_cached(self, company_name: str) -> bool:
        """Check whether clusters were already calculated for given company name"""
        # check here
        return False

    def get_data_for_analytics(self, company_name: str):
        """Collect data for analysis"""
        # TODO execute query for getting data

        return None

    def _execute_query(self, sql_query: str):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            conn.commit()
