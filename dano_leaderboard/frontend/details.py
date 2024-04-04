import yaml
from pathlib import Path

from ..constants import ASSETS_PATH

_MODELS = [
    "OpenAI GPT 4",
    "OpenAI GPT 4 Turbo",
    "OpenAI GPT 3.5 Turbo",
    "OpenAI GPT 3.5 Turbo Instruct",
    "Google Gemini Pro",
    "SOLAR 10.7B Instruct",
    "Claude Sonnet",
    "Claude Haiku",
    "Mixtral (@ Groq)",
    "Qwen1.5 7B chat",
    "OpenAI Davinci 003",
    "Heidrun Mistral 7B Chat",
    "mGPT 13B",
    "Mistral 7B Instruct (v0.2)",
    "Gemma 7B instruct",
    "Mistral 7B Instruct",
    "Heidrun Mistral 7B Base",
    "Munin NeuralBeagle 7B",
    "Gemma 7B",
    "Kanelsnegl (v. 0.2)",
    "DanskGPT-tiny Chat",
    "LlaMa 2 13B Chat",
    "Hestenettet LM",
    "OpenAI Davinci 002",
    "Munin 7B Alpha",
    "Mistral 7B",
    "LlaMa 2 7B Chat",
    "Danoliterate Mistral 7B",
    "GPT-Sw3 6.7B Instruct (v. 2)",
    "NB GPT-J NorPaca",
    "LlaMa 2 13B",
    "GPT-Sw3 6.7B (v. 2)",
    "SOLAR 10.7B",
    "LlaMa 2 7B",
    "OpenAI Babbage 002",
    "Danoliterate LlaMa 2 7B",
    "DanskGPT-tiny",
    "GPT 7B Nordic pre.",
    "GPT Neo Danish",
    "mGPT",
    "NB GPT-J",
    "Phi-2",
    "Danoliterate 7B Baseline",
    "GPT Neox Da.",
    "Constant Baseline",
]
MODELS = []
for model in _MODELS:
    with open(ASSETS_PATH / "models" / f"{model}.yaml", "r") as file:
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
