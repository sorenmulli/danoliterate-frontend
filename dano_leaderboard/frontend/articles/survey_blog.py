from dataclasses import dataclass
from datetime import datetime
import streamlit as st

from .base import BaseArticle

@dataclass
class SurveyArticle(BaseArticle):
    title: str = "Results of the Danoliterate Survey"
    date: datetime = datetime(2024, 9, 20)
    teaser: str = "Human-as-a-judge evaluation of GLLMs in Danish"

    def content(self):
        st.write("hej")
