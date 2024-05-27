import datasets

from sklearn.feature_extraction.text import TfidfVectorizer
from catboost import CatBoostClassifier

from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

from argparse import ArgumentParser, Namespace
from loguru import logger
import wandb


def parse_arguments() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("--learning_rate", type=float, default=0.05)
    parser.add_argument("--max_features", type=int, default=10000)
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--random_seed", type=int, default=1234)

    return parser.parse_args()


def load_dataset():
    paths = {
        name: f"data/sentiment/{name}.jsonl" for name in ["train", "val", "test"]
    }
    ds = datasets.load_dataset("json", data_files=paths)

    return ds


if __name__ == "__main__":
    ds = load_dataset()
    args = parse_arguments()

    wandb.init(
        project="text-clusterization",
        config={
            "approach": "tf-idf+catboost",
            "random_seed": args.random_seed
        }
    )

    # Create a pipeline that first transforms the data using TF-IDF and then fits the model
    pipeline = Pipeline([
        (
            'tfidf',
            TfidfVectorizer(
                max_features=args.max_features,
                ngram_range=(1, 2)
            )
        ),
        (
            'catboost',
            CatBoostClassifier(
                loss_function='MultiClass',
                verbose=True,
                task_type="GPU",
                devices='3',
                iterations=args.iterations,
                random_seed=args.random_seed,
                depth=args.depth,
                learning_rate=args.learning_rate,
            )
        )  # Turn off training output
    ])

    # Fit the GridSearchCV object to find the best parameters
    pipeline.fit(ds["train"]["text"], ds["train"]["sentiment"])

    for split in ["val", "test"]:
        predicted = pipeline.predict(ds[split]["text"])

        accuracy = accuracy_score(ds[split]["sentiment"], predicted)
        f1_score_micro = f1_score(ds[split]["sentiment"], predicted, average='macro')

        logger.info(f"{split} accuracy of the best model: {accuracy}")
        logger.info(f"{split} f1-score (Macro) of the best model: {f1_score_micro}")

        wandb.log(
            {
                f"{split}_accuracy": accuracy,
                f"{split}_f1_score": f1_score_micro
            }
        )
