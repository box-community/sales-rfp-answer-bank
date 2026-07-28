import os

from dotenv import load_dotenv
from box_sdk_gen import (
    BoxClient,
    CreateHubCollaborationV2025R0Hub,
    CreateHubCollaborationV2025R0AccessibleBy,
)

from box_client import get_box_client

load_dotenv()


def add_hub_collaborator(
    client: BoxClient,
    hub_id: str,
    user_email: str,
    role: str = "viewer",
):
    """Add a user to the hub. Use viewer for reps, editor for curators."""
    collaboration = client.hub_collaborations.create_hub_collaboration_v2025_r0(
        CreateHubCollaborationV2025R0Hub(id=hub_id),
        CreateHubCollaborationV2025R0AccessibleBy(
            type="user", login=user_email
        ),
        role,
    )
    print(f"Added {user_email} as {role} to hub {hub_id}")
    return collaboration


def main() -> None:
    client = get_box_client()

    hub_id = os.getenv("BOX_HUB_ID")
    if not hub_id:
        raise SystemExit(
            "BOX_HUB_ID is not set. Run python create_hub.py first, "
            "or add BOX_HUB_ID=<id> to .env."
        )

    # Replace with real sales rep emails before running.
    sales_reps = [
        email.strip()
        for email in os.getenv("SALES_REP_EMAILS", "").split(",")
        if email.strip()
    ]
    if not sales_reps:
        raise SystemExit(
            "Set SALES_REP_EMAILS in .env to a comma-separated list of "
            "emails (for example: rep1@example.com,rep2@example.com)."
        )

    for email in sales_reps:
        add_hub_collaborator(client, hub_id, email, role="viewer")


if __name__ == "__main__":
    main()
