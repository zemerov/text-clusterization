import sqlite3
import pandas as pd
import json


class DatabaseManager:
    def __init__(self, db_name: str = "data/database.db", queries_file: str = "resources/queries.sql"):
        # TODO Сделать создание и наполнение таблиц в отдельном скрипте. Таблицы создавать через явные SQL запросы, не через
        self.db_name: str = db_name

        with open(queries_file, "r") as file:
            self.queries: dict[str, str] = json.load(file)

    def save_clusters(self):
        pass

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

    def _create_database(self):
        conn = sqlite3.connect(self.db_name)
        conn.close()

    def create_table(self, df: pd.DataFrame, table_name: str):
        with sqlite3.connect(self.db_name) as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)

    def _execute_query(self, sql_query: str):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            conn.commit()
