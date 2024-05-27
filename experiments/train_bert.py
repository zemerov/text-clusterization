import datasets
import numpy as np

from argparse import ArgumentParser, Namespace
from loguru import logger
import wandb

from transformers import TrainingArguments, AutoModelForSequenceClassification, Trainer, AutoTokenizer, DataCollatorWithPadding
import evaluate


def parse_arguments() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("--learning_rate", type=float, default=5e-5)
    parser.add_argument("--adam_beta1", type=float, default=0.9)
    parser.add_argument("--adam_beta2", type=float, default=0.999)
    parser.add_argument("--warmup_steps", type=int, default=0)
    parser.add_argument("--random_seed", type=int, default=1234)
    parser.add_argument("--per_device_train_batch_size", type=int, default=64)
    parser.add_argument("--per_device_eval_batch_size", type=int, default=64)

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
            "approach": "bert",
        }
    )

    f1_score_metric = evaluate.load("f1",)

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return f1_score_metric.compute(predictions=predictions, references=labels, average="macro")

    model = AutoModelForSequenceClassification.from_pretrained("deepvk/bert-base-uncased", num_labels=3)
    tokenizer = AutoTokenizer.from_pretrained("deepvk/bert-base-uncased")

    training_args = TrainingArguments(
        output_dir="model/sentiment-bert",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        num_train_epochs=3,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        fp16=True,
        load_best_model_at_end=True,
        save_total_limit=1,
        learning_rate=args.learning_rate,
        adam_beta1=args.adam_beta1,
        adam_beta2=args.adam_beta2,
        warmup_steps=args.warmup_steps,
        logging_steps=300
    )

    ds["train"] = ds["train"].rename_column("sentiment", "label")
    ds["val"] = ds["val"].rename_column("sentiment", "label")
    ds["test"] = ds["test"].rename_column("sentiment", "label")


    def tokenize_function(example):
        return tokenizer(example["text"], truncation=True, max_length=512)


    tokenized_datasets = ds.map(tokenize_function, batched=True)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["val"],
        compute_metrics=compute_metrics,
    )

    trainer.train()

    for split in ["val", "test"]:
        predicted_metrics = trainer.evaluate(
            eval_dataset=tokenized_datasets[split]
        )
        logger.info(f"{split} f1-score (Macro) of the best model: {predicted_metrics['eval_f1']}")

        wandb.log(
            {
                f"{split}_f1_score": predicted_metrics['eval_f1']
            }
        )
