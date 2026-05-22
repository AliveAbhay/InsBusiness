import json


def load_automations():

    with open(
        "data/automations.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_comment_log(data):

    with open(
        "logs/comments.json",
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                data,
                ensure_ascii=False
            ) + "\n"
        )
