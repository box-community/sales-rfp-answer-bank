"""Live end-to-end test against a real Box enterprise.

Runs the tutorial flow with the repo's own functions:

1. create_hub.py: create a temporary hub and add the Sales Content folder.
2. refresh_hub.py: remove the folder from the hub, then add it back.
3. query_hub.py: ask the permanent, already-indexed hub in BOX_HUB_ID a
   question and check it answers.

Skips manage_access.py, which invites real users to the hub. The temporary hub
is deleted at the end; folder contents are never changed. Reads the same
variables as .env.example from the environment or a local .env.
"""

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from box_sdk_gen import AiItemAsk, CreateAiAskMode  # noqa: E402

from box_client import get_box_client  # noqa: E402
from create_hub import add_content_to_hub, create_sales_hub  # noqa: E402
from query_hub import ask_sales_question  # noqa: E402
from refresh_hub import refresh_hub_content, remove_outdated_content  # noqa: E402

REQUIRED_ENV = [
    "BOX_CLIENT_ID",
    "BOX_CLIENT_SECRET",
    "BOX_USER_ID",
    "SALES_CONTENT_FOLDER_ID",
    "BOX_HUB_ID",
]


def hub_item_ids(client, hub_id: str) -> list:
    return [item.id for item in client.hub_items.get_hub_items_v2025_r0(hub_id).entries]


def check_hub_management(client, hub_id: str, folder_id: str) -> None:
    add_content_to_hub(client, hub_id, folder_id)
    assert folder_id in hub_item_ids(client, hub_id), "Folder was not added to the hub"

    remove_outdated_content(client, hub_id, folder_id)
    assert folder_id not in hub_item_ids(client, hub_id), "Folder was not removed"

    refresh_hub_content(client, hub_id, folder_id)
    assert folder_id in hub_item_ids(client, hub_id), "Folder was not added back"


def check_ask(client) -> None:
    question = "What is our standard SLA for enterprise support?"
    hub_id = os.getenv("BOX_HUB_ID")
    answer = ask_sales_question(client, hub_id, question)
    print(f"Q: {question}\nA: {answer}")
    assert answer and answer.strip(), "Box AI returned no answer"

    # Box AI answers even from an empty hub, so require the answer to cite hub content.
    cited = client.ai.create_ai_ask(
        mode=CreateAiAskMode.SINGLE_ITEM_QA,
        prompt=question,
        items=[AiItemAsk(type="hubs", id=hub_id)],
        include_citations=True,
    )
    sources = [citation.name for citation in cited.citations or []]
    print(f"Sources: {sources}")
    assert sources, "Answer cites no hub content; check the hub is indexed"


def main() -> None:
    missing = [name for name in REQUIRED_ENV if not os.getenv(name)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)}")

    client = get_box_client()
    run_id = os.getenv("GITHUB_RUN_ID") or f"local-{int(time.time())}"
    hub_id = create_sales_hub(client, title=f"CI run {run_id}")

    try:
        check_hub_management(client, hub_id, os.getenv("SALES_CONTENT_FOLDER_ID"))
        check_ask(client)
        print("Live test passed")
    finally:
        client.hubs.delete_hub_by_id_v2025_r0(hub_id)
        print(f"Deleted hub {hub_id}")


if __name__ == "__main__":
    main()
