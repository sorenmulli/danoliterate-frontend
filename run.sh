#!/bin/bash

START_PAGE="streamlit-app/✨_Hello.py"
REPO_DIR=$(dirname "$0")

/home/swiho/.pyenv/versions/server3.11/bin/python -m streamlit run $REPO_DIR/$START_PAGE
