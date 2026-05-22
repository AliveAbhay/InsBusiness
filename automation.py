import requests

from config import (
    PAGE_ACCESS_TOKEN,
    GRAPH_API_VERSION
)


def reply_to_comment(
    comment_id,
    message
):

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/"
        f"{comment_id}/replies"
    )

    params = {
        "access_token":
        PAGE_ACCESS_TOKEN,

        "message":
        message
    }

    response = requests.post(
        url,
        params=params
    )

    print(
        "COMMENT REPLY:",
        response.text
    )
