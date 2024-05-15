import streamlit as st
from streamlit_survey import StreamlitSurvey


def build_welcome(survey: StreamlitSurvey):
    st.header("Undersøgelse af sprogmodeller på dansk")

    welcome_col, demo_col = st.columns(2)
    with welcome_col:
        st.subheader("Velkommen")
        st.info("Vil du bruge 5-10 minutter på at udforske sprogmodeller på dansk? 🤖🇩🇰", icon="ℹ️")
        st.write("""\
            Læs svar fra sprogmodeller som ChatGPT og LlaMa for at hjælpe med at vurdere, hvor godt teknologien virker på dansk.

            Spørgeskemaet giver dig mulighed for at afprøve forskellige _prompts_ (spørgsmål, instruktioner og sproglige opgaver til kunstig intelligens) og se svar fra to sprogmodeller side om side.

            Din opgave er at afprøve mindst tre prompts for hvert par af sprogmodeller og så vurdere hvilken model, der svarede bedst.
            """)
        st.divider()
        st.write("""
            Spørgeskemaet er bygget af Søren Vejlgaard Holm, Lars Kai Hansen og Martin Carsten Nielsen som en del af Danoliterate-projektet på [DTU Compute](https://www.compute.dtu.dk/) under [Pionércenteret for Kunstig Intelligens](https://www.aicentre.dk/) og i samarbejde med [Alvenir](https://www.alvenir.ai/).
            Hvis du har spørgsmål, kan du kontakte swiho@dtu.dk eller læse mere om arbejdet på [danoliterate.compute.dtu.dk](https://danoliterate.compute.dtu.dk/). """)
    with demo_col:
        st.subheader("Baggrund")
        st.write(
            "Svar på et par personlige spørgsmål for at gøre undersøgelsen mere præcis eller gå direkte videre ved at trykke `Næste` nedenfor."
        )
        survey.selectbox(
            "Køn",
            options=[
                "Mand",
                "Kvinde",
                "Ønsker ikke at svare",
            ],
            index=None,
            placeholder="Vælg køn",
        )
        survey.selectbox(
            "Aldersgruppe",
            options=[
                "1-14",
                "15-20",
                "21-34",
                "35-49",
                "50-64",
                "65+",
                "Ønsker ikke at svare",
            ],
            index=None,
            placeholder="Vælg aldersgruppe",
        )
        survey.selectbox(
            "Modersmål",
            options=[
                "Dansk",
                "Et andet sprog",
                "Ønsker ikke at svare",
            ],
            index=None,
            placeholder="Vælg modersmål",
        )
        survey.selectbox(
            "Erfaring med kunstig intelligens",
            options=[
                "Ingen erfaring",
                "Mindre erfaring",
                "Større erfaring på hobby-niveau",
                "Professionel erfaring",
                "Ønsker ikke at svare",
            ],
            index=None,
            placeholder="Vælg erfaring",
        )
