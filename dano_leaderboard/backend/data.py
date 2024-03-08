import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Metric:
    name: str
    value: float
    uncertainty: Optional[float]

    higher_is_better: bool
    N: int


@dataclass
class Result:
    model: str
    scenario: str

    executed: str
    scoring_id: str

    metrics: list[Metric]

    chosen_metric: Optional[Metric] = None

    @property
    def key(self):
        return self.model, self.scenario


@dataclass
class ResultDump:
    last_change: str
    last_commit: str

    results: list[Result]

    def serialize(self, path: Path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(asdict(self), file)

    @classmethod
    def deserialize(cls, path: Path):
        with open(path, "r", encoding="utf-8") as file:
            self_dict = json.load(file)
        for res in self_dict["results"]:
            res["metrics"] = [Metric(**vals) for vals in res["metrics"]]
        self_dict["results"] = [Result(**vals) for vals in self_dict["results"]]
        return cls(**self_dict)
