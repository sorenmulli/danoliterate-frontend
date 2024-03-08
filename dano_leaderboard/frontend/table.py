from pandas.io.formats.style import Styler
from ..backend.data import Metric, ResultDump
import pandas as pd
import numpy as np


WIN_EMOJI = "🏆"
INDEX_TITLE = WIN_EMOJI + "Avg. Index"
TOP_THREE_EMOJIS = "🥇", "🥈", "🥉"


def build_metric_table(dump: ResultDump, show_missing=False) -> pd.DataFrame:
    df = pd.DataFrame()
    for res in dump.results:
        if res.model not in df.index:
            df.loc[res.model, :] = [float("nan")] * len(df.columns)
        if res.scenario not in df.columns:
            df[res.scenario] = [float("nan")] * len(df)
        df.at[res.model, res.scenario] = res.chosen_metric
    if not show_missing:
        df = df.dropna()
    return df


def _space(val: str, spacing=5) -> str:
    return " " * (spacing - len(val)) + val


def _format_err(num):
    if round(num) >= 1:
        return f"{num:.0f}"
    else:
        num_str = str(num)
        if "." in num_str:
            decimal_part = num_str.split(".")[1]
            for i, digit in enumerate(decimal_part):
                if digit != "0":
                    return f"{num:.{i+1}f}"
        return str(num)


def calc_scenario_scores(col: pd.Series):
    vals = pd.Series([metric.value for metric in col if isinstance(metric, Metric)])
    return (vals - vals.min()) / (vals.max() - vals.min())


def calculate_index(df: pd.DataFrame, micro=True):
    index_scores = df.apply(calc_scenario_scores)

    weights = []
    for col in df.columns:
        example_metrics = [metric for metric in df[col] if isinstance(metric, Metric)]
        if example_metrics and not example_metrics[0].higher_is_better:
            index_scores[col] = 1 - index_scores[col]
        weights.append(example_metrics[0].N or 1 if example_metrics else 1)
    weights = np.array(weights)

    mean_idx = (
        index_scores.apply(
            lambda x: np.ma.average(
                np.ma.MaskedArray(x, mask=np.isnan(x)),
                weights=weights,
            ),
            axis=1,
        )
        if micro
        else index_scores.mean(axis=1)
    )

    index_scores.index = df.index
    top_threes = {
        scenario: index_scores[scenario].nlargest(3).index for scenario in index_scores.columns
    }
    return mean_idx, top_threes


def style(styler: Styler):
    styler.background_gradient(vmin=0, vmax=100, subset=[INDEX_TITLE])
    return styler


def construct_table(dump: ResultDump, micro=True, show_missing=False):
    df = build_metric_table(dump, show_missing)
    mean_idx, top_threes = calculate_index(df, micro=micro)
    df[INDEX_TITLE] = [_space(str(round(score * 100))) for score in mean_idx]
    df = df[[INDEX_TITLE, *[col for col in df.columns if col != INDEX_TITLE]]].sort_values(
        INDEX_TITLE, ascending=False
    )

    for model in df.index:
        for scenario in df.columns:
            if isinstance(metric := df[scenario][model], Metric):
                agg = _space(str(round(metric.value * 100)))
                unc = "± " + _format_err(metric.uncertainty * 100) if metric.uncertainty else ""
                df.at[model, scenario] = agg + unc
    for scenario, top_three in top_threes.items():
        for model, emoji in zip(top_three, TOP_THREE_EMOJIS):
            df.at[model, scenario] = df[scenario][model] + emoji
    return df.style.pipe(style)
