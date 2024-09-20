from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import streamlit as st

from datasets import Dataset, load_dataset

from dano_leaderboard.constants import ASSETS_PATH

from .base import BaseArticle

@st.cache_data
def get_dataset() -> Optional[Dataset]:
    try:
        return load_dataset("sorenmulli/danoliterate-survey-answers", split="train")
    except ConnectionError as error:
        print("Got connection error:", error)
        return None


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
Analysis suggests that the different automatic evaluation scenarios are correlated with each other into one, underlying factor of Danoliteracy.
Though encouraging, there is a harder question:
Is this common benchmark dimension correspondent to a meaningful factor of Danish capabilities in GLLMs, a sort of Danoliteracy $g$-factor?


Let's ask Danish speakers!

Inspired by the popular English LmSys Chatbot Arena [lmsys], we made an interactive survey site allowing Danish speakers to explore different models and prompts,
giving their own judgement of model quality.

The survey is still live at this page under ''Spørgeskema'', and if you speak Danish, please check it out!
"""
        )
        st.link_button("Check out the survey", "https://danoliterate.compute.dtu.dk/Spørgeskema")

        st.subheader("2. Methodology")
        st.write(
"""
Instead of hosting GLLMs live like the English Chatbot Arena, 100 Danish prompts were produced.
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

All are optional, containing "I don't know" as an option.

The user have a chance to get revealed what models they saw, locking their answers, before they
can go on to the next model.

All data is saved live during interaction.
""")


        st.subheader("3. Survey Results")
        # TODO: Make PNG
        # st.image(str(ASSETS_PATH /"result-significance-human-feedback.pdf"), caption="hej")
        with st.spinner("Loading newest answers..."):
            dataset = get_dataset()
        st.write(f"Number of answers: {None if dataset is None else len(dataset)}")
        st.info("More results are coming soon")

        st.subheader("4. See more")
        st.link_button("Check out the dataset of prompts", "https://huggingface.co/datasets/sorenmulli/danoliterate-survey-prompts",)
        st.link_button("Check out the dataset of replies", "https://huggingface.co/datasets/sorenmulli/danoliterate-survey-answers",)
        st.link_button("Try the survey yourself", "https://danoliterate.compute.dtu.dk/Spørgeskema")
        st.link_button("Read more about the Danoliterate project", "https://danoliterate.compute.dtu.dk")
        st.write(
"""
Literature

- [lmsys]  Lianmin Zheng, Wei-Lin Chiang, Ying Sheng et al. 2023. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. arXiv:2306.05685.

- [zao-sanders] Marc Zao-Sanders. 2024. How people are really using GenAI. Harvard Business Review.
"""
)
