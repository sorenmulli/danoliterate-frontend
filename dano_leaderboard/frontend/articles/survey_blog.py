from dataclasses import dataclass
from datetime import datetime
import streamlit as st

from datasets import load_dataset

from .base import BaseArticle


@dataclass
class SurveyArticle(BaseArticle):
    title: str = "Results of the Danoliterate Survey"
    date: datetime = datetime(2024, 9, 20)
    teaser: str = "Human-as-a-judge evaluation of GLLMs in Danish"

    def content(self):
        st.subheader("1. Survey Method")
        st.write(
            """
For 100 GLLM use-cases divided into six categories *[zao-sanders2024genai]*, we translated use-cases and categories into Danish and crafted an example prompt in Danish corresponding to that theme.
We saved model answers from 18 models and used them in the survey to allow interactiveness without requiring infrastructure for true dynamic model responses.

The survey front-end allowed volunteers to pick between the 100 prompts separated into categories, seeing model outputs from ''Model A'' and ''Model B'' side-by-side, streamed with a delay of 0.1 seconds between each word to simulate model generation.
The volunteer was then instructed to try out at least a total of three prompts before answering.
The answer consists of a question of preference, with optional additional Likert scales for each model and a text field for more details.
"""
        )

        st.subheader("2. Survey Results")
        with st.spinner("Loading answers..."):
            dataset = load_dataset("sorenmulli/danoliterate-survey-answers", split="train")
        st.write(f"Number of answers: {len(dataset)}")
