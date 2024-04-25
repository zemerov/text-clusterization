import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from wordcloud import STOPWORDS, WordCloud
import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import seaborn as sns
import random
import numpy as np
from pathlib import Path
import pandas as pd

DEFAULT_DATABASE_PATH = Path("resources")


class DataVisualizer:
    def __init__(self, plots_path: Path = DEFAULT_DATABASE_PATH):
        self.plots_path: Path = plots_path

    def top_barplot(self, df: pd.DataFrame, 
                                    x='count_reviews', 
                                    y='cluster_topic', 
                                    top=15, 
                                    title_tale = 'reviews categories', 
                                    x_title = 'Number of reviews', 
                                    file_name = 'top_clusters_barplot.png'):

        pivot_df = df.pivot_table(index=y, columns='sentiment', values=x, aggfunc='sum', fill_value=0)
        pivot_df['total_reviews'] = pivot_df.sum(axis=1)
        pivot_df = pivot_df.sort_values(by='total_reviews', ascending=False)[:top]
        pivot_df.drop(columns='total_reviews', inplace=True)
        colors = {'POSITIVE': 'green', 'NEUTRAL': 'cyan', 'NEGATIVE': 'red'}
        pivot_df = pivot_df.reindex(pivot_df.index[::-1])
        fig, ax = plt.subplots(figsize=(12, 10))
        left = np.zeros(len(pivot_df))
        row_counts = np.zeros(len(pivot_df))
        total_reviews = pivot_df.sum(axis=1)

        for i, col in enumerate(pivot_df.columns):
            counts = pivot_df[col]
            for j, (count, category) in enumerate(zip(counts, pivot_df.index)):
                percent = count / total_reviews[j] * 100
                bar = ax.barh(j, count, align='center', left=left[j], color=colors[col])
                bar_width = bar[0].get_window_extent().width
                if bar_width > 130000:
                    ax.text(left[j] + count / 2, j, f'{percent:.1f}%', ha='center', va='center', color='black')
                left[j] += count
                row_counts[j] += count

        ax.set_yticks(np.arange(len(pivot_df)))
        ax.set_yticklabels(pivot_df.index, fontsize=10)
        ax.set_xlabel(x_title, fontsize=12)
        ax.set_ylabel('')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.grid(True, axis='x', linestyle='--', alpha=0.3)
        legend_elements = [
            mpatches.Patch(color=colors['POSITIVE'], label='Positive'),
            mpatches.Patch(color=colors['NEUTRAL'], label='Neutral'),
            mpatches.Patch(color=colors['NEGATIVE'], label='Negative')
        ]
        legend_title = 'Sentiment'
        ax.legend(handles=legend_elements, loc='lower right', title=legend_title)
        plt.title((f'Top {top} ' + title_tale), fontweight='bold', loc='left', fontsize=12)
        plt.tight_layout()
        plt.savefig(self.plots_path / file_name, bbox_inches='tight', pad_inches=0.1)
    
    def ver_bar_chart(self, df, 
                             title='Reviews by sentiment', 
                             top=None, 
                             file_name = 'sentiments_barplot.png'):
        sns.set_style("white")
        fig, ax = plt.subplots(figsize=(6, 4))
        if top is not None:
            df = df.nlargest(top, 'count')
        categories = df['sentiment']
        counts = df['count']
        colors = {'POSITIVE': 'green', 'NEUTRAL': 'cyan', 'NEGATIVE': 'red'}
        palette = [colors[sentiment] for sentiment in categories]
        ax = sns.barplot(x=categories, y=counts, palette=palette)
        for i, count in enumerate(counts):
            ax.text(i, count, str(count), ha='center', va='bottom')
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_xlabel('')  
        ax.set_ylabel('')  
        ax.set_yticks([])  
        ax.set_title(title)
        plt.savefig(self.plots_path / file_name, bbox_inches='tight', pad_inches=0.1)

    def words_clouds(self, df: pd.DataFrame):
        stopwords = set(STOPWORDS)
        stopwords.update(["есть", 'может'])
        unique_sentiments = df['sentiment'].unique()
        colors = {
            'POSITIVE': px.colors.sequential.algae,
            'NEUTRAL': px.colors.sequential.Mint,
            'NEGATIVE': px.colors.sequential.Reds
        }

        for sentiment_value in unique_sentiments:
            file_name = f'wordcloud_sentiment_{sentiment_value}.png'
            sentiment_df = df[df['sentiment'] == sentiment_value]
            sentiment_text = " ".join(sentiment_df['reviews'].tolist())
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

            width, height = wordcloud.width, wordcloud.height
            fig = make_subplots(rows=1, cols=1)
            fig.add_trace(
                go.Image(z=wordcloud.to_array()),
                row=1, col=1
            )
            fig.update_layout(
                title=f"Sentiment: {sentiment_value}",
                margin=dict(l=15, r=15, t=40, b=20),
                paper_bgcolor='white',
                width=width,
                height=height,
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False)
            )
            pio.write_image(fig, self.plots_path / f'wordcloud_sentiment_{sentiment_value}.png')
