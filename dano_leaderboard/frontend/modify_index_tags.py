import streamlit as st
from bs4 import BeautifulSoup
from pathlib import Path

def modify_tag_content(tag_name: str, new_content: str):
    # Source for this:
    # https://discuss.streamlit.io/t/updating-title-description-of-app-in-google-search/61447/5
    index_path = Path(st.__file__).parent / "static" / "index.html"
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")

    if not (backup := index_path.with_suffix(".bck")).exists():
        backup.write_text(str(soup))

    if (target_tag := soup.find(tag_name)):
        target_tag.string = new_content
    else:
        target_tag = soup.new_tag(tag_name)
        target_tag.string = new_content
        if tag_name in {"title", "script", "noscript"} and soup.head:
            soup.head.append(target_tag)
        elif soup.body:
            soup.body.append(target_tag)
    index_path.write_text(str(soup))


if __name__ == "__main__":
    # To fix title in Google Search and links
    modify_tag_content("title", "The Danoliterate Generative Large Language Model Benchmark")
    modify_tag_content("noscript",
        "The Danoliterate Benchmark from the Technical University of Denmark. "
        "Evaluating models like GPT-4, LlaMa and Claude in Danish. "
        "See learderboards, take the survey, read articles and inspect further result details. "
        "You need to enable JavaScript to run this app. "
    )
