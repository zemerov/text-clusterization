import pandas as pd


class Loader:
    def __init__(self, source_path: str, minimum_threshold: int = 10):
        self.data = pd.read_json(source_path, lines=True)
        self.minimum_threshold = minimum_threshold

    def get_data(self, rubric: str, company_name: str) -> pd.DataFrame:
        all_data = self.data[self.data["rubric"] == rubric]
        # company_data = all_data[all_data["name_ru"] == company_name]
        #
        # all_data = {k: list(v) for k, v in all_data.items()}
        # company_data = {k: list(v) for k, v in company_data.items()}
        #
        # if len(all_data) < self.minimum_threshold:
        #     raise ValueError(f"Not enough comments for rubric: {rubric}. Please choose more common rubric.")
        #
        # if len(company_data) < self.minimum_threshold:
        #     raise ValueError(
        #         f"Not enough comments to analyze for company: {company_name}. Please choose another company")

        return all_data
