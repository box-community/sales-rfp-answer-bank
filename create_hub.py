import os

from dotenv import load_dotenv
from box_sdk_gen import (
    BoxClient,
    FolderReferenceV2025R0,
    HubItemOperationV2025R0,
    HubItemOperationV2025R0ActionField,
)

from box_client import get_box_client

load_dotenv()


def create_sales_hub(
    client: BoxClient,
    title: str = "Sales RFP Answer Bank",
) -> str:
    """Provision a new Sales Hub and return its ID."""
    hub = client.hubs.create_hub_v2025_r0(
        title,
        description=(
            "Curated library of approved proposals, RFP responses, "
            "competitive intelligence, and pricing materials for the sales team."
        ),
    )

    print(f"Created hub: {hub.title} (ID: {hub.id})")
    return hub.id


def add_content_to_hub(
    client: BoxClient, hub_id: str, folder_id: str
) -> None:
    """Add a folder (and its contents) to the hub."""
    client.hub_items.manage_hub_items_v2025_r0(
        hub_id,
        operations=[
            HubItemOperationV2025R0(
                action=HubItemOperationV2025R0ActionField.ADD,
                item=FolderReferenceV2025R0(id=folder_id),
            )
        ],
    )
    print(f"Added folder {folder_id} to hub {hub_id}")


def _persist_hub_id(hub_id: str) -> None:
    """Write or update BOX_HUB_ID in .env so other scripts can reuse it."""
    env_path = ".env"
    line = f"BOX_HUB_ID={hub_id}\n"
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(line)
        return

    with open(env_path, encoding="utf-8") as f:
        lines = f.readlines()

    updated = False
    for i, existing in enumerate(lines):
        if existing.startswith("BOX_HUB_ID="):
            lines[i] = line
            updated = True
            break
    if not updated:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.append(line)

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def main() -> None:
    client = get_box_client()

    hub_id = create_sales_hub(client)

    sales_folder_id = os.getenv("SALES_CONTENT_FOLDER_ID")
    if not sales_folder_id:
        raise SystemExit(
            "SALES_CONTENT_FOLDER_ID is not set in .env. "
            "Upload sample_content/ to Box, then set the folder ID."
        )

    add_content_to_hub(client, hub_id, sales_folder_id)
    _persist_hub_id(hub_id)

    print(f"\nSales Hub ready. Hub ID: {hub_id}")
    print("BOX_HUB_ID was written to .env for query_hub.py and manage_access.py.")
    print("Share this hub with your sales team or embed it in your CRM.")
    print(
        "Wait a few minutes for indexing before running: python query_hub.py"
    )


if __name__ == "__main__":
    main()
