import pandas as pd
import sqlite3
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import plotly.io as pio

class DataVisualizer:
    def __init__(self, database_path):
        self.database_path = database_path

    def get_data(self, query):
        conn = sqlite3.connect(self.database_path)  # Исправлено
        df = pd.read_sql_query(query, conn)
        df.reset_index(drop=True, inplace=True)
        conn.close()
        return df

    def get_plot_top_categories(self, df, col_quantity, col_category, title, title_x_axis, title_y_axis, top_n, title_font_size=12, categories_font_size=9, numbers_font_size=11):
        # Получаем топ-N записей
        df_top = df.sort_values(by=col_quantity, ascending=False).head(top_n)

        # Создаем график
        f, ax = plt.subplots(figsize=(8, 6), facecolor='none')  # Изменяем размер фигуры
        ax.patch.set_facecolor('none')
        sns.set_color_codes("colorblind")

        colors = {'POSITIVE': 'green', 'NEUTRAL': 'cyan', 'NEGATIVE': 'red'}
        barplot = sns.barplot(x=col_quantity, y=col_category, data=df_top, hue="sentiment", palette=colors, dodge=False, ax=ax)

        for p in ax.patches:
            ax.text(p.get_width() / 2, p.get_y() + p.get_height() / 2, "%.0f" % p.get_width(), fontsize=numbers_font_size, ha='center', va='center')

        sns.despine(left=True, bottom=True)
        ax.legend(title='Sentiment', loc="lower right")
        ax.set_title(title, fontweight='bold', loc='left', fontsize=title_font_size)

        new_patches = []
        for patch in reversed(ax.patches):
            bb = patch.get_bbox()
            color = patch.get_facecolor()
            p_bbox = FancyBboxPatch((bb.xmin, bb.ymin),
                                    abs(bb.width), abs(bb.height),
                                    boxstyle="round,pad=-0.1,rounding_size=1.1",
                                    ec="none", fc=color,
                                    mutation_aspect=0.2 
                                    )
            patch.remove()
            new_patches.append(p_bbox)

        for patch in new_patches:
            ax.add_patch(patch)

        # Устанавливаем подписи для осей
        ax.set_ylabel(title_y_axis, fontsize=title_font_size)
        ax.set_xlabel(title_x_axis, fontsize=title_font_size)
        
        # Устанавливаем метки для оси X
        ax.set_xticklabels(df_top[col_quantity], fontsize=numbers_font_size)
        
        # Убираем деления на оси X
        ax.xaxis.set_ticks_position('none')
        
        ax.set_xticks([])
        ax.tick_params(axis='y', length=0, labelsize=categories_font_size)
        plt.tight_layout()

        return ax


    def get_coordinates_nominatim(self, address):
        base_url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        try: 
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Ошибка при запросе координат: {e}")
            return None, None

        if len(data) == 0:
            return None, None

        latitude = float(data[0]['lat'])
        longitude = float(data[0]['lon'])

        return latitude, longitude

    def plot_map_from_database(self, city_name, filename):  # Убран database_path
        # Координаты города по его названию
        city_coordinates = self.get_coordinates_nominatim(city_name)  # Исправлено
        if city_coordinates is None:
            print(f"Ошибка: Невозможно определить координаты города {city_name}")
            return

        comments_df = self.get_data("SELECT address, COUNT(*) as count, avg(CASE WHEN sentiment = 'NEGATIVE' THEN -1 WHEN sentiment = 'NEUTRAL' THEN 0 WHEN sentiment = 'POSITIVE' THEN 1 END) AS sentiment_numeric FROM comments GROUP BY address")

        # Координаты для каждого адреса
        comments_df['latitude'] = None
        comments_df['longitude'] = None
        for index, row in comments_df.iterrows():
            latitude, longitude = self.get_coordinates_nominatim(row['address'])  # Исправлено
            comments_df.at[index, 'latitude'] = latitude
            comments_df.at[index, 'longitude'] = longitude

        comments_df = comments_df.dropna(subset=['latitude', 'longitude'])

        fig = px.scatter_mapbox(comments_df, lat="latitude", lon="longitude", size="count", zoom=10,
                                center=dict(lat=city_coordinates[0], lon=city_coordinates[1]),
                                color="sentiment_numeric", color_continuous_scale=px.colors.diverging.RdYlGn,
                                color_continuous_midpoint=0)
        fig.update_layout(mapbox_style="carto-positron")

        pio.write_html(fig, filename)

