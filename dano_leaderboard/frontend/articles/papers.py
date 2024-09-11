from dataclasses import dataclass
from datetime import datetime
import streamlit as st

from .base import BaseArticle

@dataclass
class ThesisArticle(BaseArticle):
    title: str = "Are GLLMs Danoliterate? Benchmarking Generative NLP in Danish"
    date: datetime = datetime(2024, 1, 15)
    teaser: str = "Original Master's thesis"

    def content(self):
        st.write("Read the original Master's thesis at [sorenmulli.github.io/thesis/thesis.pdf](https://sorenmulli.github.io/thesis/thesis.pdf)")


