import json
from argparse import ArgumentParser
from pathlib import Path
from dano_leaderboard.frontend.survey.infrastructure import OUTPUT_DIR as SURVEY_DATA_DIR

OUTPUT_FILE = "survey-data.jsonl"
ANSWER_FIELDS = "prefer", "likert-A", "likert-B", "text"


def main(input_dir: str, output_file: str):
    print("Extracting survey data from %s to %s" % (input_dir, output_file))
    data_examples = []

    ids, ids_with_content, model_pairs, output_examples = 0, 0, 0, 0
    for user_id in Path(input_dir).glob("*"):
        if not user_id.is_dir():
            continue
        ids += 1
        try:
            newest = next(iter(sorted(user_id.glob("*.json"))[::-1]))
        except StopIteration:
            continue
        ids_with_content += 1
        data = json.loads(newest.read_text())
        common_data = {
            "user-gender": data["answers"]["Køn"]["value"],
            "user-age": data["answers"]["Aldersgruppe"]["value"],
            "user-language": data["answers"]["Modersmål"]["value"],
            "user-experience": data["answers"]["Erfaring med kunstig intelligens"]["value"],
            "session-id": data["user_id"],
            "session-all-chosen-models": data["chosen_models"],
            "session-all-was-revelead": data["was_revealed"],
            "session-all-seen-prompts": data["seen_prompts"],
            "session-timestamp": newest.stem,
        }
        for i, models in enumerate(data["chosen_models"]):
            model_pairs += 1
            models_key = " ".join(models)
            models_data = {
                field: data["answers"][key]["value"].replace("🤖", "").strip()
                for field in ANSWER_FIELDS
                if (key := f"{models_key}-{field}") in data["answers"]
            }
            if any(models_data.values()):
                output_examples += 1
                data_examples.append(
                    {
                        "model_A": models[0],
                        "model_B": models[1],
                        **models_data,
                        "seen_prompts": data["seen_prompts"][models_key],
                        "index": i,
                        "was_revealed": data["was_revealed"][models_key],
                        **common_data,
                    }
                )
    print(
        f"Extracted {output_examples} examples from {model_pairs} model pairs of {ids_with_content} sessions with data from {ids} total sessions"
    )
    Path(output_file).write_text("".join(json.dumps(ex) + "\n" for ex in data_examples))
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--input-dir", type=str, default=SURVEY_DATA_DIR)
    parser.add_argument("--output-file", type=str, default=OUTPUT_FILE)
    args = parser.parse_args()
    main(args.input_dir, args.output_file)
