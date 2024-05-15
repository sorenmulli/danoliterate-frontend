import logging
from pathlib import Path

PAIRS_TO_SHOW = 5
MIN_PROMPTS = 3

STREAM_SLEEP = 0.1

OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "survey-data"

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="survey-server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
)
