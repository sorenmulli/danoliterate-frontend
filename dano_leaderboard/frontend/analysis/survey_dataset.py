from itertools import combinations

import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import numpy as np
from scipy.stats import norm
from scipy import stats
import networkx as nx
from matplotlib import pyplot as plt


RENAME = {
    None: "       N/A",
    "": "               N/A",
    "Mand": "Male",
    "Kvinde": "Female",
    "Professionel erfaring": "  Professional",
    "Mindre erfaring": "    Lesser",
    "Større erfaring på hobby-niveau": "   Greater",
    "Ingen erfaring": "     None",
    "Dansk": " Danish",
    "Et andet sprog": " Another Language",
    "Ved ikke": " Don't know",
}

BASE = 10
PRETTY_NAMES = {
    "mhenrichsen/danskgpt-tiny-chat": "DanskGPT-tiny Chat",
    "Qwen/Qwen1.5-7B-Chat": "Qwen1.5 7B Chat",
    "RJuro/munin-neuralbeagle-7b": "Munin NeuralBeagle",
    "upstage/SOLAR-10.7B-Instruct-v1.0": "SOLAR 10.7B In.",
    "mistralai/Mistral-7B-Instruct-v0.2": "Mistral 7B In. v0.2",
    "llama3-8b-8192": "LlaMa 3 8B In.",
    "google/gemma-7b-it": "Gemma 7B In.",
    "llama3-70b-8192": "LlaMa 3 70B",
    "mixtral-8x7b-32768": "Mixtral 8x7B",
    "Mabeck/Heidrun-Mistral-7B-chat": "Heidrun 7B Chat",
    "Nexusflow/Starling-LM-7B-beta": "Starling 7B",
    "gpt-3.5-turbo-0125": "GPT 3.5 Turbo",
    "claude-3-sonnet-20240229": "Claude Sonnet",
    "gpt-4-turbo": "GPT 4 Turbo 2024",
    "claude-3-haiku-20240307": "Claude Haiku",
    "gemini-pro": "Gemini Pro",
    "gpt-4o": "GPT 4o",
    "claude-3-opus-20240229": "Claude Opus",
}


def plot_demographics(
    ax, df, column, title, valuesort=False, rotation=45, ylim=True, density=False
):
    total = len(df)
    df = df.copy()
    if column != "user-age":
        df[column] = df[column].apply(lambda k: RENAME.get(k, k))

    sns.countplot(
        data=df,
        x=column,
        order=sorted(x for x in df[column].unique() if not pd.isna(x))
        if valuesort
        else df[column].value_counts().index,
        ax=ax,
    )
    ax.set_xlabel("")
    ax.set_title(title)
    ax.set_ylabel("Density" if density else "Count")
    if ylim:
        ax.set_ylim(0, total + 10)
    ax.tick_params(axis="x", rotation=rotation)

    # Adding percentage annotations on top of the bars
    for p in ax.patches:
        height = p.get_height()
        percentage = f"{height / total:.0%}"
        ax.annotate(
            percentage,
            (p.get_x() + p.get_width() / 2.0, height),
            ha="center",
            va="center",
            xytext=(0, 9),
            textcoords="offset points",
        )


def compute_bradley_terry(df: pd.DataFrame) -> pd.DataFrame:
    ptbl_a_win = pd.pivot_table(
        df[df["prefer"] == "A"],
        index="model_A",
        columns="model_B",
        aggfunc="size",
        fill_value=0,
    )

    ptbl_b_win = pd.pivot_table(
        df[df["prefer"] == "B"],
        index="model_A",
        columns="model_B",
        aggfunc="size",
        fill_value=0,
    )
    ptbl_win = ptbl_a_win * 2 + ptbl_b_win.T * 2

    models = pd.Series(np.arange(len(ptbl_win.index)), index=ptbl_win.index)

    n_combinations = len(models) * (len(models) - 1) * 2
    X = np.zeros((n_combinations, len(models)))
    Y = np.zeros(n_combinations)

    reward = np.log(BASE)
    i = 0
    sample_weights = []
    for m_a in ptbl_win.index:
        for m_b in ptbl_win.columns:
            if m_a == m_b:
                continue
            X[i, models[m_a]] = reward
            X[i, models[m_b]] = -reward
            Y[i] = 1.0
            sample_weights.append(ptbl_win.loc[m_a, m_b])

            X[i + 1, models[m_a]] = reward
            X[i + 1, models[m_b]] = -reward
            Y[i + 1] = 0.0
            sample_weights.append(ptbl_win.loc[m_b, m_a])
            i += 2
    model = sm.GLM(Y, X, family=sm.families.Binomial(), freq_weights=sample_weights)
    results = model.fit()
    return pd.DataFrame(
        {"BT coefficient": results.params, "SE": results.bse}, index=models.index.values
    ).sort_values(by="BT coefficient", ascending=False)


def visualize_bradley_terry_ranking(std_bt_board: pd.DataFrame, alpha=0.05):
    min_ci = -1
    max_ci = 1
    bt_index = std_bt_board["BT coefficient"].apply(
        lambda x: (x - min_ci) / (max_ci - min_ci)
    )

    combination_significant = {}
    ps = []
    for one, other in combinations(std_bt_board.index, 2):
        coef1, se1 = std_bt_board.loc[one]
        coef2, se2 = std_bt_board.loc[other]
        diff = coef1 - coef2
        se_diff = np.sqrt(se1**2 + se2**2)
        ps.append(2 * (1 - norm.cdf(abs(diff / se_diff))))

    ps = stats.false_discovery_control(ps, method="bh")
    for p, (one, other) in zip(ps, combinations(std_bt_board.index, 2), strict=True):
        combination_significant[(one, other)] = p < alpha

    G = nx.Graph()
    G.add_nodes_from(
        [node for node, _ in std_bt_board.sort_values("BT coefficient").iterrows()]
    )
    for (model1, model2), significant in combination_significant.items():
        if not significant and model1 in G.nodes and model2 in G.nodes:
            G.add_edge(model1, model2)

    radius_increase = 1.2
    pos = nx.circular_layout(G, center=[0, 0])
    label_pos = {
        name: coord * (np.linalg.norm(coord) * radius_increase) / np.linalg.norm(coord)
        for name, coord in pos.items()
    }

    fig, axis = plt.subplots(figsize=(7, 7))

    nx.draw_networkx_labels(
        G,
        label_pos,
        {
            node: " ".join(
                "\n" + ch if i % 2 else ch
                for i, ch in enumerate(PRETTY_NAMES[node].replace("-", " ").split())
            )
            for node in G
        },
        font_size=10,
        font_family="serif",
    )
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=12,
        labels={n: int(bt_index[n] * 100) for n in G},
        font_family="serif",
    )

    vmax, vmin = (1.1, -0.1)
    nx.draw_networkx(
        G,
        pos,
        labels={},
        node_color=[bt_index[node] for node in G.nodes],
        cmap=plt.cm.Spectral,
        connectionstyle="arc3,rad=-0.2",
        arrows=True,
        vmax=vmax,
        vmin=vmin,
        node_size=1000,
    )
    plt.axis("off")
    axis.text(
        0,
        0,
        "Human Feedback Ranking\nBradley-Terry Model",
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=15,
    )
    axis.set_xlim([1.2 * x for x in axis.get_xlim()])
    axis.set_ylim([1.2 * y for y in axis.get_ylim()])
    fig.tight_layout()
    return fig
