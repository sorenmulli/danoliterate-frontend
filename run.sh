#!/bin/bash

START_PAGE="streamlit-app/🇩🇰_Hello.py"
REPO_DIR=$(dirname "$0")

streamlit run $REPO_DIR/$START_PAGE
