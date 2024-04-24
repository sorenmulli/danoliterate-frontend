import yaml
from pathlib import Path

from ..constants import ASSETS_PATH

MODELS = []
for path in (ASSETS_PATH / "models").glob("*.yaml"):
    with path.open("r") as file:
        MODELS.append(yaml.safe_load(file))
MODEL_DICT = {model["model"]: model for model in MODELS}
DIMENSIONS_TO_HIDE_MODELS = {
    "Capability": {},
    "Efficiency": {
        "Mixtral (@ Groq)",
        "Constant Baseline",
        *[model for model, details in MODEL_DICT.items() if details.get("closed", True)],
    },
    "Calibration": {},
    "Toxicity": {},
}

_SCENARIOS = [
    "Citizenship Test",
    "HyggeSwag",
    "#twitterhjerne",
    "Da. Cloze Self Test",
    "Da. Gym 2000",
    "Nordjylland News",
    "DaNE",
    "Angry Tweets",
]
SCENARIOS = []
for scenario in _SCENARIOS:
    with open(ASSETS_PATH / "scenarios" / f"{scenario}.yaml", "r") as file:
        SCENARIOS.append(yaml.safe_load(file))

_METRICS = [
    "Accuracy (NLG Parsing of chosen option)",
    "Accuracy (LM)",
    "NER F1",
    "Prediction odd-one-out frequency (BERT similarity)",
    "Prediction odd-one-out frequency (ROUGE-L)",
    "Prediction odd-one-out frequency (ROUGE-1)",
    "Avg. similarity to references (BERT similarity)",
    "Avg. similarity to references (ROUGE-L)",
    "Avg. similarity to references (ROUGE-1)",
    "Similarity (BERT similarity)",
    "Similarity (ROUGE-L)",
    "Similarity (ROUGE-1)",
    "Inference seconds",
    "Brier Score (LM)",
    "ECE Calibration (LM)",
    "Generated Text Offensive Prob",
]
METRICS = []
for metric in _METRICS:
    with open(ASSETS_PATH / "metrics" / f"{metric}.yaml", "r") as file:
        METRICS.append(yaml.safe_load(file))
METRIC_DICT = {metric["metric"]: metric for metric in METRICS}
