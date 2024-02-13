import os
from openai import OpenAI
from numpy.random import choice
from loguru import logger
from tqdm.auto import tqdm


class OpenAIAPIWrapper:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model

        logger.info(f"Set up OpenAI API wrapper for model {model}")

    def _construct_prompt(self, comments: list[str], keywords: str) -> str:
        prompt = f"""Какие выводы можно сделать по этиму кластеру отзывов пользователей?
        
        Ключевые слова для кластера: {keywords}
        Отзывы пользователей:
        """

        for i, x in enumerate(comments):
            prompt += f"{i + 1}. {x.strip()}.\n"

        prompt += "В ответ напиши один ключевой вывод."

        return prompt

    def get_cluster_summary(
        self, all_comments: list[str], keywords: str, total_samples: int = 7
    ) -> str:
        comments = choice(
            all_comments, replace=False, size=min(total_samples, len(all_comments))
        )
        prompt = self._construct_prompt(comments, keywords)

        logger.info(f"Sending request for the prompt:\n{prompt[:100]}...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        answer = response.choices[0].message.content

        logger.info(f"Got cluster summary: {answer[:200]}...")
        logger.info(
            f"Total tokens: {response.usage.total_tokens};\
              Prompt tokens: {response.usage.prompt_tokens};\
              Completion tokens: {response.usage.completion_tokens}"
        )

        return answer

    def get_cluster_summaries(
        self, topics, comments, topics_info, parallel: int = 1
    ) -> dict[int, str]:
        # TODO add parallel requests
        cluster_summaries = {}

        for cluster_id in tqdm(
            range(len(set(topics)) - 1), desc="Generating cluster summaries"
        ):
            cluster_comments = comments[comments["topics"] == cluster_id][
                "text"
            ].tolist()

            cluster_summaries[cluster_id] = self.get_cluster_summary(
                cluster_comments, topics_info[cluster_id]
            )

        return cluster_summaries
