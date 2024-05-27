import pandas as pd
from loguru import logger


class Loader:
    COLUMN_TO_SUBJECT = {"rubrics": "rubrics", "name_ru": "company name"}

    def __init__(self, source_path: str, minimum_threshold: int = 10):
        self.data = pd.read_json(source_path, lines=True)
        self.minimum_threshold = minimum_threshold

        logger.info(
            f"Loaded dataframe from {source_path}. Dataset size: {len(self.data)}"
        )

    def get_company_comments(self, company_name: str) -> pd.DataFrame:
        return self._get_data_by_column(company_name, "name_ru")

    def get_rubric_comments(self, rubric: str) -> pd.DataFrame:
        return self._get_data_by_column(rubric, "rubrics")

    def _get_data_by_column(self, value: str, col_name: str) -> pd.DataFrame:
        data = self.data[self.data[col_name] == value]
        name = Loader.COLUMN_TO_SUBJECT.get(col_name, None)

        logger.info(f"Loaded {len(data)} samples for {name}: {value}")

        if len(data) < self.minimum_threshold:
            raise ValueError(
                f"Not enough comments for rubric: {value}. Please choose more common {name}."
            )

        return data
