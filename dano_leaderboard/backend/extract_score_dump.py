import json
from pathlib import Path

from .data import Metric, Result, ResultDump


def parse_scoring(scoring: dict) -> Result:
    metrics = [
        Metric(
            metric["short_name"],
            metric["aggregate"],
            metric["error"],
            metric["higher_is_better"],
            len(metric["example_results"]),
        )
        for metric in scoring["metric_results"]
    ]
    return Result(
        model=scoring["execution_metadata"]["model_cfg"]["name"],
        scenario=scoring["execution_metadata"]["scenario_cfg"]["name"],
        scoring_id=scoring["id_"],
        executed=scoring["execution_metadata"]["timestamp"],
        metrics=metrics,
    )


def unique_res(results: list[Result]) -> list[Result]:
    unique_results: dict[tuple, Result] = {}
    for res in results:
        if res.key not in unique_results or unique_results[res.key].executed < res.executed:
            unique_results[res.key] = res
    return list(unique_results.values())


def extract(in_path: Path, out_path: Path):
    print("Reading scores from %s, outputting to %s" % (in_path, out_path))
    with open(in_path, "r", encoding="utf-8") as file:
        scorings = json.load(file)["scorings"]
    print("Loaded %i scorings" % (N := len(scorings)))
    newest_score = sorted(scorings, key=lambda s: s["timestamp"])[-1]
    dump = ResultDump(
        last_change=newest_score["timestamp"],
        last_commit=newest_score["commit"],
        results=[],
    )
    scorings = [
        scoring
        for scoring in scorings
        if scoring["execution_metadata"]["scenario_cfg"].get("type", "standard") == "standard"
    ]
    print("Removed %i scorings with experimental types" % (N - (N := len(scorings))))
    scorings = [
        scoring for scoring in scorings if scoring["execution_metadata"]["augmenter_key"] is None
    ]
    print("Removed %i augmented scorings" % (N - (N := len(scorings))))
    meta_results: list[Result] = []
    normal_results: list[Result] = []
    for scoring in scorings:
        res = parse_scoring(scoring)
        if scoring.get("is_meta"):
            meta_results.append(res)
        else:
            normal_results.append(res)
    print("Got %i normal results and %i meta results" % (len(normal_results), len(meta_results)))

    normal_results = unique_res(normal_results)
    meta_results = unique_res(meta_results)
    print(
        "Removed %i duplicate normal results" % (N - (N := len(normal_results) + len(meta_results)))
    )

    normal_res_dict = {res.key: res for res in normal_results}
    for meta in meta_results:
        try:
            normal = normal_res_dict[meta.key]
        except KeyError as error:
            raise ValueError(
                f"You have not run the normal capability version of {meta.key}"
            ) from error
        for metric in meta.metrics:
            if any(metric.name == other_metric.name for other_metric in normal.metrics):
                raise ValueError
            normal.metrics.append(metric)

    print("Added %i meta results" % len(meta_results))
    dump.results = normal_results
    print("Finally got %i results" % len(dump.results))
    dump.serialize(out_path)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("in_path")
    parser.add_argument("out_path")
    args = parser.parse_args()
    extract(Path(args.in_path), Path(args.out_path))
