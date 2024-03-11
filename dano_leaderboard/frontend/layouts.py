from collections import defaultdict
import streamlit as st
import pandas as pd

from ..backend.data import Result, ResultDump
from ..constants import ASSETS_PATH, RESULT_PATH
from .result_parsing import DIMENSIONS_TO_METRICS, select_results
from .table import CLOSED_EMOJI, INSTRUCT_EMOJI, LINK_EMOJI, WIN_EMOJI, construct_table
from .details import METRIC_DICT, MODELS, SCENARIOS


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
    with open(ASSETS_PATH / "hello.md", "r", encoding="utf-8") as file:
        hello_content = file.read()
    st.write(hello_content)


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
        for scenario_dict in SCENARIOS:
            scenario = scenario_dict["scenario"]
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
                    options,
                    index=options.index(result_group[0].chosen_metric.name),
                    key=scenario + model_names,
                )
                for res in result_group:
                    res.chosen_metric = next(
                        metric for metric in res.metrics if metric.name == selected_metric
                    )
                st.caption(
                    f"Currently showing: {selected_metric}.",
                    help=METRIC_DICT[selected_metric]["description"]
                    if selected_metric in METRIC_DICT
                    else "",
                )
        st.form_submit_button(label="Submit")


def build_leaderboard():
    set_global_style(wide=True)
    st.title("Danoliterate GLLM Leaderboard")
    st.warning(
        "The benchmark is still work-in-progress."
        " Evaluation dimensions beyond capability are experimental",
        icon="⌛",
    )
    st.write(
        f"""
- Visit the 🇩🇰 Hello page to get an overview of what this is.
- Note that the below table can be expanded.
- Hover over table column headers for more details.
- See left sidebar for metric details and to change displayed metrics.
- Visit the 📚 Scenarios page to read about each evaluation scenario.
- Visit the 🤖 Models page to read about tested models.
"""
    )

    result_dump = fetch_results_cached()

    show_missing = st.checkbox("Include models with missing values")
    index_type = st.selectbox("Index Average", ["Micro Avg.", "Macro Avg."])
    index_micro = index_type == "Micro Avg."
    chosen_dimension = (
        st.selectbox("Evaluation Dimension", DIMENSIONS_TO_METRICS.keys())
        or list(DIMENSIONS_TO_METRICS.keys())[0]
    )
    select_results(result_dump, chosen_dimension)
    build_metric_selection_sidebar(result_dump.results)
    table = construct_table(result_dump, index_micro, show_missing)
    st.dataframe(
        table,
        use_container_width=True,
        column_config={
            INSTRUCT_EMOJI: st.column_config.Column(
                help="Checked if model has been instruct-tuned."
            ),
            CLOSED_EMOJI: st.column_config.Column(
                help="Checked if model weights have not been made openly available."
            ),
            WIN_EMOJI: st.column_config.Column(
                help=f"{index_type} of scenario index scores where 100=best, 0=worst."
            ),
            LINK_EMOJI: st.column_config.LinkColumn(help="Link to model details."),
            **{
                scenario["scenario"]: st.column_config.Column(help=scenario["description"])
                for scenario in SCENARIOS
            },
        },
    )


def build_scenarios():
    set_global_style()
    st.title("Danoliterate Benchmark Scenarios")
    st.write(
        """
Read descriptions of scenarios used for the benchmark.

See examples of data and prompting on the 🔎Examples page.

For more details, read the original Master's thesis chapters 4.2 and 5.3: [''Are GLLMs Danoliterate? Benchmarking Generative NLP in Danish''](https://sorenmulli.github.io/thesis/thesis.pdf).
"""
    )
    for scenario in SCENARIOS:
        st.subheader(scenario["scenario"])
        st.caption(scenario["description"])
        col1, col2 = st.columns(2)
        col1.metric(label="Number of Examples", value=scenario["N"])
        col2.page_link(scenario["link"], label="Dataset Card", icon="🤗")
        st.write(scenario["details"])
        st.divider()


def build_models():
    set_global_style()
    st.title("Danoliterate Benchmarked GLLMs")
    st.write(
        """
See below for description of evaluated models.
To be sure to get accurate details, consult original model creators.
"""
    )
    for model in MODELS:
        st.subheader(model["model"])
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            "Openly Available?",
            value="No" if model["closed"] else "Yes",
            delta="Weights inaccesible" if model["closed"] else "Open-source weights",
            delta_color="inverse" if model["closed"] else "normal",
        )
        col2.metric("Instruct-tuned?", value="Yes" if model["instruct"] else "No")
        col3.metric("Parameter Count [Billions]", value=model.get("params"))
        if link := model.get("link"):
            col4.page_link(link, label="Model link", icon="🤗" if "huggingface" in link else "🔗")
        st.write(model["description"])
        st.divider()


def build_examples():
    set_global_style()
    st.title("Danoliterate GLLM Prediction Examples")
    st.write(
        """
Inspect some model outputs on the benchmark from selected models.
"""
    )
    scenarios = {
        scenario.stem.replace(".csv", ""): pd.read_csv(scenario, index_col=0)
        for scenario in sorted((ASSETS_PATH / "example-outputs").resolve().glob("*.csv"))
    }
    chosen_scenario = (
        st.selectbox("Scenario", [scenario["scenario"] for scenario in SCENARIOS])
        or SCENARIOS[0]["scenario"]
    )
    data = scenarios[chosen_scenario]
    chosen_model = st.selectbox("Model", [col for col in data.columns if col != "prompt"])
    if st.button("Show output examples"):
        for label, row in data.iterrows():
            st.markdown(f"### Prompt {label}")
            st.code(row["prompt"], language=None)
            st.markdown(f"### {chosen_model} Generation {label}")
            st.code(row[chosen_model], language=None)
            st.divider()
