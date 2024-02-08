import sqlite3
import pandas as pd

class DatabaseMaker:
    def __init__(self, db_name='Database.db'):
        self.db_name = db_name

    def create_database(self):
        conn = sqlite3.connect(self.db_name)
        conn.close()

    def create_reviews_table(self, df):
        conn = sqlite3.connect(self.db_name)
        df.to_sql('reviews', conn, if_exists='replace', index=False)
        conn.close()

    def create_clusters_table(self, df):
        conn = sqlite3.connect(self.db_name)
        df.to_sql('clusters', conn, if_exists='replace', index=False)
        conn.close()

    def link_tables(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS reviews_clusters_link (
                            review_id INTEGER,
                            cluster_id INTEGER,
                            FOREIGN KEY(review_id) REFERENCES reviews(cluster_id),
                            FOREIGN KEY(cluster_id) REFERENCES clusters(id)
                        )''')
        conn.commit()
        conn.close()