import pandas as pd
import sqlite3

from database_manager import DEFAULT_DATABASE_PATH


create_geo_comments = """CREATE TABLE IF NOT EXISTS geo_comments (
id INTEGER PRIMARY KEY,
name VARCHAR,
address VARCHAR,
rating INT,
rubric VARCHAR,
text VARCHAR);"""

create_comments_analysis = """CREATE TABLE IF NOT EXISTS comments_analysis (
id INTEGER PRIMARY KEY,
cluster_id INTEGER,
sentiment VARCHAR,
FOREIGN KEY (id) REFERENCES geo_comments(id)
);"""

create_clusters = """CREATE TABLE IF NOT EXISTS clusters (
name VARCHAR,
cluster_id VARCHAR,
keywords TEXT,
description VARCHAR,
FOREIGN KEY (name) REFERENCES geo_comments(name),
PRIMARY KEY (name, cluster_id)
);"""


if __name__ == "__main__":
    # Create tables
    with sqlite3.connect(DEFAULT_DATABASE_PATH) as conn:
        cursor = conn.cursor()
        for query in [create_geo_comments, create_comments_analysis, create_clusters]:
            cursor.execute(query)
        conn.commit()

    # Insert data to geo_comments table
    geo_comments_table = pd.read_json("data/geo-reviews-dataset-2023-full.jsonl", lines=True)
    geo_comments_table = geo_comments_table[['name_ru', 'address', 'rating', 'rubrics', 'text']]
    geo_comments_table.columns = ['name', 'address', 'rating', 'rubric', 'text']
    geo_comments_table["id"] = geo_comments_table.index

    with sqlite3.connect(DEFAULT_DATABASE_PATH) as conn:
        cursor = conn.cursor()
        geo_comments_table.to_sql('geo_comments', conn, if_exists='append', index=False)
        conn.commit()

    print("Done!")
