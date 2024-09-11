from dataclasses import dataclass
from datetime import datetime
import streamlit as st

from .base import BaseArticle

@dataclass
class VidenAiArticle(BaseArticle):
    title: str = "Omtale: viden.ai [Da.]"
    date: datetime = datetime(2024, 5, 27)
    teaser: str = "Anbefaling af spørgeskema"

    def content(self):
        st.write("Se omtalen på [viden.ai/nyhedsbreve/ugens-nyheder-farlige-og-forkerte-svar-fra-googles-ai](https://viden.ai/nyhedsbreve/ugens-nyheder-farlige-og-forkerte-svar-fra-googles-ai/#dtu)")



@dataclass
class SprogteknologiArticle(BaseArticle):
    title: str = "Omtale: Sprogteknologi.dk [Da.]"
    date: datetime = datetime(2024, 7, 1)
    teaser: str = "Interview og fokus på spørgeskema"

    def content(self):
        st.write("Se omtalen på [sprogteknologi.dk/blog/danoliterate](https://sprogteknologi.dk/blog/danoliterate)")
