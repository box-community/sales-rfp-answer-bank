import os
import sys

from dotenv import load_dotenv
from box_sdk_gen import (
    BoxClient,
    CreateAiAskMode,
    AiItemAsk,
)

from box_client import get_box_client

load_dotenv()


def ask_sales_question(
    client: BoxClient, hub_id: str, question: str
) -> str:
    """Ask Box AI a question grounded in the hub's indexed content."""
    response = client.ai.create_ai_ask(
        mode=CreateAiAskMode.SINGLE_ITEM_QA,
        prompt=question,
        items=[
            AiItemAsk(
                type="hubs",
                id=hub_id,
            )
        ],
    )

    return response.answer


def main() -> None:
    client = get_box_client()

    hub_id = os.getenv("BOX_HUB_ID")
    if not hub_id:
        raise SystemExit(
            "BOX_HUB_ID is not set. Run python create_hub.py first, "
            "or add BOX_HUB_ID=<id> to .env."
        )

    # Pass a question on the command line, or run the default set.
    if len(sys.argv) > 1:
        questions = [" ".join(sys.argv[1:])]
    else:
        questions = [
            "What is our standard SLA for enterprise support?",
            "How do we handle data residency requirements for EU customers?",
            "What security certifications do we hold?",
            "What discount tiers are available for 500+ seat deals?",
        ]

    for question in questions:
        print(f"\nQ: {question}")
        answer = ask_sales_question(client, hub_id, question)
        print(f"A: {answer}")


if __name__ == "__main__":
    main()
