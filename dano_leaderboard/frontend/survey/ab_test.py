from typing import Optional

from streamlit_survey.pages import Pages
from streamlit_survey import StreamlitSurvey

import time

import streamlit as st

from .infrastructure import MIN_PROMPTS, PAIRS_TO_SHOW, STREAM_SLEEP, logger


def _color_cat(text: str, category: str) -> str:
    match category[0]:
        case "R":
            return f":green[{text}]"
        case "F":
            return f":red[{text}]"
        case "P":
            return f":violet[{text}]"
        case "L":
            return f":orange[{text}]"
        case "S":
            return f":blue[{text}]"
        case "T":
            return f"**{text}**"
    return text


def build_prompt_choice(
    models: tuple[str, str], examples: list[dict]
) -> tuple[Optional[int], bool]:
    st.subheader("1. Vælg prompts")
    st.caption("Udforsk de seks kategorier og vælg en prompt, der interesserer dig.")
    new_chosen = False
    chosen_prompt = (
        None
        if not st.session_state["seen_prompts"][models]
        else st.session_state["seen_prompts"][models][-1]
    )
    categories = st.session_state["category_order"]
    tabs = st.tabs([_color_cat(cat, cat) for cat in categories])
    for cat, tab in zip(categories, tabs):
        n = 1
        with tab, st.container(height=250, border=False):
            for ex_idx in st.session_state["example_order"]:
                example = examples[ex_idx]
                if example["category"] != cat:
                    continue

                with st.popover(
                    _color_cat(f"Prompt {n}:", cat) + " " + example["use_case"],
                    use_container_width=True,
                ):
                    popover = st.empty()
                    with popover.container():
                        st.write(example["prompt"].replace("\n", "\n\n"))
                        choose_prompt = st.button(
                            "Prøv prompten", key=" ".join(models) + str(ex_idx)
                        )
                    if choose_prompt:
                        popover.caption("Se svaret nedenfor.")

                        st.session_state["seen_prompts"][models].append(ex_idx)
                        chosen_prompt = ex_idx
                        new_chosen = True

                n += 1
    return chosen_prompt, new_chosen


def build_model_answers(
    chosen_prompt: Optional[int], new_chosen: bool, models: tuple[str, str], examples: list[dict]
):
    if chosen_prompt is None:
        with st.chat_message("user"):
            st.write("...")
    else:
        with st.chat_message("user"):
            st.write(examples[chosen_prompt]["prompt"])
        for col, model, emoji in zip(st.columns(2), models, "🇦🇧"):

            def stream_data(sleep=True):
                for i, word in enumerate(examples[chosen_prompt]["models"][model].split(" ")):
                    yield word + " "
                    if sleep:
                        if i < 120:
                            time.sleep(STREAM_SLEEP)
                        else:
                            time.sleep(STREAM_SLEEP / 10)

            with col, st.container(border=True):
                with st.chat_message("assistant"):
                    st.write(f"**Model {emoji}**:\n")
                    if new_chosen:
                        st.write_stream(stream_data())
                    else:
                        st.write_stream(stream_data(sleep=False))


def build_answer(models: tuple[str, str], survey: StreamlitSurvey, pages: Pages):
    st.subheader("3. Giv din vurdering")
    has_seen = len(set(st.session_state["seen_prompts"][models]))
    was_revealed = st.session_state["was_revealed"][models]
    if has_seen < MIN_PROMPTS:
        progress_text = f"Du har kun set :orange[{has_seen}] forskellige eksempler. Se mindst :blue[{MIN_PROMPTS}] for at bedømme."
    else:
        extra = " og du har fået afsløret modellerne." if was_revealed else "."
        progress_text = f"Du har set {has_seen} forskellige eksempler for disse modeller" + extra
    st.progress(min(has_seen / MIN_PROMPTS, 1.0), text=progress_text)
    do_disable = was_revealed or has_seen < MIN_PROMPTS

    with st.container(border=True):
        survey.radio(
            "Hvilken model foretrak du?",
            options=["🤖A", "🤖B", "Ved ikke"],
            id=" ".join(models) + "-prefer",
            horizontal=True,
            index=None,
            disabled=do_disable,
        )
    survey.radio(
        "Hvad synes du om 🤖 A?",
        options=["😞", "🙁", "😐", "🙂", "😀", "Ved ikke"],
        id=" ".join(models) + "-likert-A",
        horizontal=True,
        index=None,
        disabled=do_disable,
    )
    survey.radio(
        "Hvad synes du om 🤖 B?",
        options=["😞", "🙁", "😐", "🙂", "😀", "Ved ikke"],
        id=" ".join(models) + "-likert-B",
        horizontal=True,
        index=None,
        disabled=do_disable,
    )
    survey.text_input(
        "Evt. uddybende tekst:",
        id=" ".join(models) + "-text",
        disabled=do_disable,
    )

    nav_area = st.container()
    pages.nav_context = nav_area

    if has_seen >= MIN_PROMPTS and survey.data[" ".join(models) + "-prefer"]["value"] is not None:
        if st.button("Afslør modellerne (låser dine svar)", disabled=was_revealed):
            st.session_state["was_revealed"][models] = True
            st.rerun()
    if was_revealed:
        st.write(f"🤖 A var '{models[0]}'.\n\n🤖 B var '{models[1]}'")


def show_status_message(survey: StreamlitSurvey, pair_idx: int):
    if not pair_idx:
        st.info(
            "Nu er der i hemmelighed valgt to modeller for dig: 🤖A og 🤖B.\n\n Afprøv dem ved at vælge en prompt under en kategori, der interesserer dig."
            " Se modellernes svar og få et indtryk af både A og B. Vælg nu en ny prompt og giv endelig din vurdering efter mindst 3 prompts."
        )
        return
    prev_models_key = " ".join(st.session_state["chosen_models"][pair_idx - 1]) + "-prefer"
    if prev_models_key in survey.data and survey.data[prev_models_key]["value"] is not None:
        success_emojis = "🔥 ", "🎇 ", "🎆 ", "👌 ", "🙌 "
        succes_emoji = success_emojis[pair_idx - 1] if pair_idx <= len(success_emojis) else ""
        st.success(
            succes_emoji
            + f"Tak! Din besvarelse for par {pair_idx} er gemt og indsendt. Her er det næste par."
        )
    else:
        st.warning(
            f"Du valgte ikke foretrukken model for par {pair_idx}, men du har stadig mulighed for at trykke tilbage og give din vurdering."
        )


def build_ab_test(examples: list[dict], survey: StreamlitSurvey, pages: Pages):
    pair_idx = pages.current - 1
    models = st.session_state["chosen_models"][pair_idx]
    logger.debug("Displaying models %s and %s", *models)

    st.header(f"Hemmeligt par af sprogmodeller #:orange[{pair_idx + 1}] ud af {PAIRS_TO_SHOW} 🤖")
    show_status_message(survey, pair_idx)
    choose_col, answer_col = st.columns([2, 1])
    st.divider()
    model_area = st.container()
    with choose_col:
        chosen_prompt, new_chosen = build_prompt_choice(models, examples)
    with model_area:
        st.subheader("2. Se modellernes svar")
        build_model_answers(chosen_prompt, new_chosen, models, examples)
        if len(st.session_state["seen_prompts"][models]) > 1:
            with st.expander("Se tidligere svar"):
                for i, prompt in enumerate(st.session_state["seen_prompts"][models][:-1]):
                    if i:
                        st.divider()
                    build_model_answers(prompt, False, models, examples)
        if chosen_prompt is not None:
            st.caption("Fortsæt ved at gå til toppen af siden igen.")
    with answer_col:
        build_answer(models, survey, pages)
