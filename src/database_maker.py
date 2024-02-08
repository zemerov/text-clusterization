import sqlite3
import pandas as pd


class DatabaseMaker:
    def __init__(self, db_name: str = "data/database.db"):
        self.db_name: str = db_name

    def create_database(self):
        conn = sqlite3.connect(self.db_name)
        conn.close()

    def create_table(self, df: pd.DataFrame, table_name: str):
        with sqlite3.connect(self.db_name) as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)

    def link_tables(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS reviews_clusters_link (
                                review_id INTEGER,
                                cluster_id INTEGER,
                                FOREIGN KEY(review_id) REFERENCES reviews(cluster_id),
                                FOREIGN KEY(cluster_id) REFERENCES clusters(id)
                            )"""
            )
            conn.commit()
