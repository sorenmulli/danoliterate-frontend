from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4
from random import shuffle

import numpy as np
import streamlit as st
import streamlit_survey as ss

from .ab_test import build_ab_test
from .welcome import build_welcome
from .infrastructure import OUTPUT_DIR, PAIRS_TO_SHOW, logger


def fetch_model_answers_cached():
    return [
        json.loads(line)
        for line in (Path(__file__).parent.parent.parent / "assets" / "prompts.jsonl")
        .read_text()
        .split("\n")
        if line.strip()
    ]


def set_up_state() -> list[dict]:
    examples: list[dict] = fetch_model_answers_cached()
    all_models: list[str] = list(examples[0]["models"].keys())
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid4())

    if "chosen_models" not in st.session_state:
        if len(all_models) < 2 * PAIRS_TO_SHOW:
            raise ValueError("Too few models!")
        st.session_state["chosen_models"] = [
            tuple(models)
            for models in np.random.choice(
                all_models,
                size=2 * PAIRS_TO_SHOW,
                replace=False,
            ).reshape(-1, 2)
        ]
        logger.info(
            "User %s got models %s",
            st.session_state["user_id"],
            ", ".join(str(models) for models in st.session_state["chosen_models"]),
        )
    if "seen_prompts" not in st.session_state:
        st.session_state["seen_prompts"] = {
            models: [] for models in st.session_state["chosen_models"]
        }
    if "was_revealed" not in st.session_state:
        st.session_state["was_revealed"] = {
            models: False for models in st.session_state["chosen_models"]
        }
    if "category_order" not in st.session_state:
        categories = sorted(set(example["category"] for example in examples))
        shuffle(categories)
        st.session_state["category_order"] = categories
    if "example_order" not in st.session_state:
        example_order = list(range(len(examples)))
        shuffle(example_order)
        st.session_state["example_order"] = example_order
    examples = [examples[i] for i in st.session_state["example_order"]]
    return examples


def save_state(survey: ss.StreamlitSurvey):
    user_path: Path = OUTPUT_DIR / st.session_state["user_id"]
    user_path.mkdir(exist_ok=True)

    output_data = {
        "answers": survey.data,
        "user_id": st.session_state["user_id"],
        "chosen_models": st.session_state["chosen_models"],
        "seen_prompts": {
            " ".join(models): val for models, val in st.session_state["seen_prompts"].items()
        },
        "was_revealed": {
            " ".join(models): val for models, val in st.session_state["was_revealed"].items()
        },
    }

    this_path = user_path / (datetime.now().strftime("%Y%m%d-%H%M%S") + ".json")
    this_path.write_text(json.dumps(output_data))


@st.experimental_dialog("Tak!")
def goodbye_dialog():
    st.success(
        "Din besvarelse er gemt.\n"
        "Tusind tak for dit bidrag til undersøgelse af kunstig intelligens på dansk!\n"
        "Tøv ikke med at dele undersøgelsen."
    )
    st.page_link("✨_Hello.py", label="➡️ Projektforside")


def goodbye(survey: ss.StreamlitSurvey):
    save_state(survey)
    st.balloons()
    goodbye_dialog()


def build_survey_pages():
    survey = ss.StreamlitSurvey("dano-llm-eval")
    examples = set_up_state()
    pages = survey.pages(PAIRS_TO_SHOW + 1, on_submit=lambda: goodbye(survey))
    pages.progress_bar = False
    pages.prev_button = lambda pages: st.button(
        "Tilbage",
        use_container_width=True,
        disabled=pages.current == 0,
        on_click=pages.previous,
        key=f"{pages.current_page_key}_btn_prev",
    )
    pages.next_button = lambda pages: st.button(
        "Næste",
        type="primary",
        use_container_width=True,
        on_click=pages.next,
        disabled=pages.current == pages.n_pages - 1,
        key=f"{pages.current_page_key}_btn_next",
    )
    pages.submit_button = lambda pages: st.button(
        "Indsend",
        type="primary",
        use_container_width=True,
        key=f"{pages.current_page_key}_btn_submit",
    )

    with pages:
        if pages.current == 0:
            build_welcome(survey)
        else:
            build_ab_test(examples, survey, pages)
        save_state(survey)
