from ..backend.data import Result, ResultDump
from .details import DIMENSIONS_TO_HIDE_MODELS, MODEL_DICT


DIMENSIONS_TO_METRICS = {
    "Capability": [
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
    ],
    "Efficiency": [
        "Inference seconds",
    ],
    "Calibration": [
        "Brier Score (LM)",
        "ECE Calibration (LM)",
    ],
    "Toxicity": [
        "Generated Text Offensive Prob",
    ],
}


def filter_available(result: Result, dimension: str):
    approved_metrics = DIMENSIONS_TO_METRICS[dimension]
    filtered_metrics = [metric for metric in result.metrics if metric.name in approved_metrics]
    if result.model in DIMENSIONS_TO_HIDE_MODELS[dimension]:
        return []
    return sorted(filtered_metrics, key=lambda metric: approved_metrics.index(metric.name))


def select_results(dump: ResultDump, dimension: str):
    filtered_results: list[Result] = []
    for res in dump.results:
        res.metrics = filter_available(res, dimension)
        if res.metrics:
            res.chosen_metric = res.metrics[0]
            filtered_results.append(res)
    dump.results = filtered_results
