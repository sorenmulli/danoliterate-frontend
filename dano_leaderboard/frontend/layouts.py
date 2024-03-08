from collections import defaultdict
from pathlib import Path
import streamlit as st

from ..backend.data import Result, ResultDump
from .result_parsing import DIMENSIONS_TO_METRICS, SCENARIOS, select_results
from .table import construct_table

RESULT_PATH = Path("out.json")


def set_global_style(wide=False):
    st.set_page_config(
        "Danoliterate Benchmark", page_icon="🇩🇰", layout="wide" if wide else "centered"
    )
    # Source for this:
    # https://discuss.streamlit.io/t/remove-made-with-streamlit-from-bottom-of-app/1370/17
    hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def build_hello():
    set_global_style()
    st.title("Danoliterate GLLMs")
    st.warning("The benchmark is a beta version and results are subject to change.", icon="🤖")

    st.write(
        """
## What is this?
This site presents the :sparkles: Danoliterate Generative Large Language Model Benchmark :sparkles:, evaluating how well models like ChatGPT, LlaMa or Mistral perform in Danish.
## Where can I see it?
Press `leaderboard` in the left sidebar to see how the models were ranked.
To inspect some specific examples of what the models generate, press `examples`.
## How can I learn more?
Currently, the main documentation for this benchmark is the Master's Thesis
[''Are GLLMs Danoliterate? Benchmarking Generative NLP in Danish''](https://sorenmulli.github.io/thesis/thesis.pdf).
The implementation is open and can be found on [sorenmulli/danoliterate](https://github.com/sorenmulli/danoliterate):
Please follow along and participate!
## Who made this?
This is part of a Master's Thesis produced by Søren Vejlgaard Holm at the DTU Compute in collaboration with [Alvenir](https://www.alvenir.ai/).
It was supervised by
- Lars Kai Hansen, DTU Compute

- Martin Carsten Nielsen, Alvenir

The work was supported by the Pioneer Centre for AI.
"""
    )


@st.cache_data
def fetch_results_cached() -> ResultDump:
    return ResultDump.deserialize(RESULT_PATH)


def group_results_by_metrics(results: list[Result]):
    metrics_to_models = defaultdict(list)
    for res in results:
        metrics_to_models[tuple(metric.name for metric in res.metrics)].append(res)
    return metrics_to_models


def build_metric_selection_sidebar(results: list[Result]):
    with st.sidebar, st.form(key="metric_selection"):
        for scenario in SCENARIOS:
            scenario_res = [res for res in results if res.scenario == scenario]
            if not scenario_res:
                continue
            st.subheader(f"Choose :blue[{scenario}] Metrics")
            result_groups = group_results_by_metrics(scenario_res)
            for metrics, result_group in result_groups.items():
                options = list(metrics)
                model_names = (
                    "All Models"
                    if len(result_groups) == 1
                    else "Rest of Models"
                    if len(result_groups) == 2
                    and len(result_group) > sum(len(group) for group in result_groups.values()) // 2
                    else ", ".join(res.model for res in result_group)
                )
                selected_metric = st.selectbox(
                    f"Metric for {model_names}",
                    list(metrics),
                    index=options.index(result_group[0].chosen_metric.name),
                    key=scenario + model_names,
                )
                for res in result_group:
                    res.chosen_metric = next(
                        metric for metric in res.metrics if metric.name == selected_metric
                    )
                st.caption(f"Currently showing: {selected_metric}.")
        st.form_submit_button(label="Submit")


def build_leaderboard():
    set_global_style(wide=True)
    st.title("Danoliterate GLLM Leaderboard")
    st.warning(
        "The benchmark is a beta version and results are subject to change. Especially toxicity, robustness and fairness are experimental solutions.",
        icon="🤖",
    )
    st.write(
        """
Go to the 🇩🇰Hello page to get more details about what is going on.
Note that the table can be expanded.
"""
    )

    result_dump = fetch_results_cached()

    show_missing = st.checkbox("Include models with missing values")
    index_micro = st.selectbox("Index Average", ["Micro Avg.", "Macro Avg."]) == "Micro Avg."
    chosen_dimension = (
        st.selectbox("Evaluation Dimension", DIMENSIONS_TO_METRICS.keys())
        or list(DIMENSIONS_TO_METRICS.keys())[0]
    )
    select_results(result_dump, chosen_dimension)
    build_metric_selection_sidebar(result_dump.results)
    table = construct_table(result_dump, index_micro, show_missing)
    st.dataframe(table, use_container_width=True)
