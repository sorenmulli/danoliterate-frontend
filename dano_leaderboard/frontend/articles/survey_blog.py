from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from threading import Lock

import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from datasets import load_dataset

plt_lock = Lock()


from .base import BaseArticle
from ..analysis.survey_dataset import (
    plot_demographics,
    compute_bradley_terry,
    visualize_bradley_terry_ranking,
)


@st.cache_data
def get_dataset() -> Optional[pd.DataFrame]:
    try:
        return pd.DataFrame(
            load_dataset("sorenmulli/danoliterate-survey-answers", split="train")
        )
    except ConnectionError as error:
        print("Got connection error:", error)
        return None


def display_results(survey_df):
    survey_models = list(
        set(np.concatenate((survey_df["model_A"], survey_df["model_B"])))
    )
    st.write(
        "So far, we have collected `%i` A/B tests for `%i` models from `%i` unique users"
        % (len(survey_df), len(survey_models), len(survey_df["session-id"].unique()))
    )
    grouped_df = survey_df.groupby("session-id").first().reset_index()
    st.write(
        "Many of these are male, young, and have a high level of experience in GLLMs:"
    )
    with plt_lock:
        fig, axes = plt.subplots(2, 2, figsize=(6, 6))
        plot_demographics(
            axes[0, 0],
            grouped_df,
            "user-gender",
            "Gender Distribution",
            density=True,
            valuesort=True,
        )
        plot_demographics(
            axes[0, 1], grouped_df, "user-age", "Age Group Distribution", valuesort=True
        )
        plot_demographics(
            axes[1, 0],
            grouped_df,
            "user-language",
            "1st Language Distribution",
            valuesort=True,
        )
        plot_demographics(
            axes[1, 1],
            grouped_df,
            "user-experience",
            "User Experience Distribution",
            valuesort=True,
        )
        fig.tight_layout()
        st.pyplot(fig)

    st.write("Future expansion of the survey should target a wider demographic.")
    st.write("Let's go to some high-level impressions from their answers:")

    with plt_lock:
        fig, axes = plt.subplots(2, 2, figsize=(6, 6))
        plot_demographics(axes[0][0], survey_df, "prefer", "Global Preferences")
        plot_demographics(
            axes[0][1],
            pd.DataFrame(
                {
                    "likert": survey_df["likert-B"].tolist()
                    + survey_df["likert-A"].tolist()
                }
            ),
            "likert",
            "Global Likert Scores",
            valuesort=True,
        )
        plot_demographics(
            axes[1][0],
            pd.DataFrame(
                {
                    "n_seen_prompts": [
                        len(prompts)
                        for prompts in survey_df["seen_prompts"]
                        if prompts is not None
                    ]
                }
            ),
            "n_seen_prompts",
            "Number of Seen Prompts",
            valuesort=True,
        )
        plot_demographics(axes[1][1], survey_df, "index", "A/B Test Session Index")
        fig.tight_layout()
        st.pyplot(fig)
    st.write(
        "On the inputs, people are able to decide a winner in most cases and, nicely, give well symmetrically distributed scores. "
        "Most users see the required 3 prompts, other keep going and see more before choosing a winner. "
        "Finally, we see that most results come from the first A/B test of a user with only about half of users completing more than one: "
        " though most that complete more than one then also complete all suggested four"
    )
    st.write(
        "But the most interesting thing: *The ranking!* "
        f"We have a dataset of `{len(survey_df)}` pairwise preferences and want to transform that into one overall ranking."
        "This classical problem in the literature of learning to rank is approached by the authors of the LmSys Chatbot Arena "
        "using the Bradley-Terry model [chiang-et-al]. The central modelling decision is to estimate the probablity that model $m_A$ "
        "is preferred over model $m_B$ logistically as"
    )
    st.latex(r"P(m_A \succ m_B) = \frac{1}{1 + \exp(-(\theta_{m_A} - \theta_{m_B}))}.")
    st.write(
        r"Where $\theta_{m_A}, \theta_{m_B}$ are learned nonparametrically from the data using maximum likelihood estimation "
        " following Section 4 and Appendix B in [chiang-et-al] which we verified using their open-source implementation."
    )
    bradley_terry_results = compute_bradley_terry(survey_df)
    st.write(
        r"The coefficient $\theta_m$ thus induces a ranking (higher is better) as well as an uncertainty, shown below"
    )
    # TODO: Consider to prettify table
    st.dataframe(bradley_terry_results)
    st.write(
            "Below these results are visualized. They are scaled from [-1, 1] to [0, 100] and pairwise statistical significance is shown: "
            "If there is no significant difference at $\\alpha=0.05$ between two models, their nodes are connected. "
            "The pairwise tests have been Benjamini-Hochberg corrected for multiple comparisons."
    )
    with plt_lock:
        fig = visualize_bradley_terry_ranking(bradley_terry_results)
        st.pyplot(fig)


@dataclass
class SurveyArticle(BaseArticle):
    title: str = "Results of the Danoliterate Survey"
    date: datetime = datetime(2024, 9, 20)
    teaser: str = "Human-as-a-judge evaluation of GLLMs in Danish"

    def content(self):
        st.subheader("1. Introduction")
        st.write(
            """
The Danoliterate benchmark automatically evaluates Generative Large, Language models on Danish.
Analyzing these results, we have found that the different evaluation scenarios are correlated with each other into one, underlying factor of Danoliteracy.
This is encouraging for the benchmarking of GLLMs in Danish, but it is not enough:
Does our found factor actually descirbe something meaningful?
Have we found a real-world dimension of Danish capabilities, a sort of Danoliteracy $g$-factor?


Let's ask Danish speakers!

Inspired by the popular, primarily English-language [LmSys Chatbot Arena](https://lmarena.ai/) [lmsys], we made an interactive survey site allowing Danish speakers to explore different models and prompts,
giving their own judgement of model quality.

The survey is still live at this page under ''Spørgeskema'', and if you speak Danish, please check it out!
"""
        )
        st.link_button(
            "Check out the survey", "https://danoliterate.compute.dtu.dk/Spørgeskema"
        )

        st.subheader("2. Survey Design")
        st.write(
            """
Instead of hosting GLLMs live like the English Chatbot Arena, 100 Danish prompts were pre-generated.
These were based on 100 popular Generative AI use-cases according to [zao-sanders].
For each of these, we translated the category and use-case to Danish and manually produced a Danish-language
prompt corresponding to this description.

Now, for all 100 prompts, outputs of 18 GLLMs, both open-source and closed were computed and saved.

When users go to the interactive survey site, they are presented with a number of A/B tests between
two secret models: A and B.
The users can then freely select between the 100 prompts divided into 7 categories presented in random order and
see the output of the two secret models generated one word at a time to simulate a real-time chat experience.

The user is required to see outputs on at least three prompts before they can fill out their judgement consisting of

1. A preference: A vs. B.

2. A 5-point Likert scale.

3. A text box.

All are optional, containing "I don't know" or leaving it empty as options.

After filling out their judgement, the user can choose to get revealed what models they saw, locking their answers,
and continue to a next A/B test.

All data is saved live during interaction.
"""
        )

        st.subheader("3. Survey Results")
        with st.spinner("Loading newest answers..."):
            survey_df = get_dataset()
        if survey_df is not None:
            display_results(survey_df)

        st.subheader("4. Conclusions")
        st.write(
            """
The results show a significant ranking with different tiers of models.
Claude models from Anthropic AI generally rank higher in the human preferences than in the automatic benchmark.
Like the automatic benchmark, the open-source models lack behind OpenAI, Google and Anthropic GLLMs.

The comparison to the automatic benchmark is a crucial result of the survey: Can we trust scenario-based
benchmarking to give a good indication of human preferences?
Not too bad, it seems!
For the October 2024 version of automatic and survey benchmark results, we see a rank correlation of $\\rho \\sim 0.8.$.
Automatic benchmarking appears to be a useful tool for this technology.

However, the survey is small-scale and with a narrow user group:
With more responses and respondents that more accurately reflect Danish speakers and thus more accurately
reflect those that will be impacted by this technology, we can learn much more about how humans preference
and GLLM performance interact in Danish.

Amongst the many potential research question with more data are:

- How do gender, age, and experience in GLLMs impact preferences?

- Do users prefer some models for some categories of prompts and others for other tasks?

- When are users in doubt and why?

- Are there signals in model outputs that correlate with user preference?

So please, help improve our understanding of this disruptive technology in Danish by taking the survey
and spreading the word!
"""
        )

        st.subheader("5. See more")
        st.link_button(
            "Check out the dataset of prompts",
            "https://huggingface.co/datasets/sorenmulli/danoliterate-survey-prompts",
        )
        st.link_button(
            "Check out the dataset of replies",
            "https://huggingface.co/datasets/sorenmulli/danoliterate-survey-answers",
        )
        st.link_button(
            "Try the survey yourself", "https://danoliterate.compute.dtu.dk/Spørgeskema"
        )
        st.link_button(
            "Read more about the Danoliterate project",
            "https://danoliterate.compute.dtu.dk",
        )
        st.write(
            """
Literature

- [lmsys]  Lianmin Zheng, Wei-Lin Chiang, Ying Sheng et al. 2023. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. [arXiv:2306.05685](https://arxiv.org/abs/2306.05685).

- [chiang-et-al] Wei-Lin Chiang, Lianmin Zheng, Yiang Sheng et al. 2024. Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference. [arXiv:2403.04132](https://arxiv.org/abs/2403.04132).

- [zao-sanders] Marc Zao-Sanders. 2024. How people are really using GenAI. [Harvard Business Review](https://hbr.org/2024/03/how-people-are-really-using-genai).
"""
        )
