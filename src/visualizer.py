import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import STOPWORDS, WordCloud
import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import random

DEFAULT_DATABASE_PATH = "'resources/'"

class DataVisualizer:
    def __init__(self, company_name, plots_path: str = DEFAULT_DATABASE_PATH):
        self.plots_path : str = plots_path
        self.company_name = company_name

    def top_clusters_barplot(self, df, top=15):
        pivot_df = df.pivot_table(index='cluster_topic', columns='sentiment', values='count_reviews', aggfunc='sum', fill_value=0)
        pivot_df['total_reviews'] = pivot_df.sum(axis=1)
        pivot_df = pivot_df.sort_values(by='total_reviews', ascending=False)[:top]
        pivot_df.drop(columns='total_reviews', inplace=True)

        colors = {'POSITIVE': 'green', 'NEUTRAL': 'cyan', 'NEGATIVE': 'red'}

        pivot_df = pivot_df.reindex(pivot_df.index[::-1])
        
        fig, ax = plt.subplots(figsize=(10, 8))

        left = np.zeros(len(pivot_df))
        row_counts = np.zeros(len(pivot_df))

        total_reviews = pivot_df.sum(axis=1)

        for i, col in enumerate(pivot_df.columns):
            counts = pivot_df[col]

            for j, (count, category) in enumerate(zip(counts, pivot_df.index)):
                percent = count / total_reviews[j] * 100
                if count >= 130:  # Проверяем, если количество отзывов больше или равно 5, показываем подпись
                    ax.barh(j, count, align='center', left=left[j], color=colors[col])
                    ax.text(left[j] + count / 2, j, f'{percent:.1f}%', ha='center', va='center', color='black')
                else:  # Если количество отзывов меньше 5, не показываем подпись
                    ax.barh(j, count, align='center', left=left[j], color=colors[col])
                left[j] += count
                row_counts[j] += count

        ax.set_yticks(np.arange(len(pivot_df)))
        ax.set_yticklabels(pivot_df.index)
        ax.set_xlabel('Number of reviews')
        ax.set_ylabel('')
        plt.title(f'Top {top} reviews categories', fontweight='bold', loc='left', fontsize=12)
        filename = self.plots_path + 'top_clusters_barplot.png'
        plt.savefig(filename)

    def words_clouds(self, df):
        text = " ".join(review for review in df['reviews'])
        stopwords = set(STOPWORDS)
        stopwords.update(["есть", 'может'])
        
        # Создаем отдельные облака слов для каждого уникального значения столбца sentiment
        unique_sentiments = df['sentiment'].unique()
        colors = {'POSITIVE': px.colors.sequential.algae, 'NEUTRAL': px.colors.sequential.Mint, 'NEGATIVE': px.colors.sequential.Reds}
        for sentiment_value in unique_sentiments:
            sentiment_df = df[df['sentiment'] == sentiment_value]
            sentiment_text = " ".join(review for review in sentiment_df[column])
            wordcloud = WordCloud(
                stopwords=stopwords,
                background_color="white",
                min_word_length=4,
                collocation_threshold=10,
                scale=3,
                width=700,
                height=500,
            ).generate(sentiment_text)

            color_range = colors[sentiment_value]
            wordcloud = wordcloud.recolor(
                color_func=lambda *args, **kwargs: random.choice(color_range))

            # get the dimensions of the word cloud image
            width, height = wordcloud.width, wordcloud.height
            # create a figure using Plotly's make_subplots function
            fig = make_subplots(rows=1, cols=1)
            # add the word cloud trace to the figure
            fig.add_trace(
                go.Image(z=wordcloud.to_array()),
                row=1, col=1
            )
            # configure the layout of the figure
            fig.update_layout(
                title=f"Sentiment: {sentiment_value}",
                margin=dict(l=15, r=15, t=40, b=20),
                paper_bgcolor='white',
                width=width,
                height=height,
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False)
            )
            # сохраняем каждый график в виде изображения
            file_name = self.plots_path + f'wordcloud_sentiment_{sentiment_value}.png'
            pio.write_image(fig, file_name)

