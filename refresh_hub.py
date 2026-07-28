"""Reference helpers for keeping hub content fresh.

Integrate these into your application when sales content changes.
Adding a top-level folder indexes its files and subfolders; new files
added to those folders in Box are picked up automatically.
"""

from box_sdk_gen import (
    BoxClient,
    FolderReferenceV2025R0,
    HubItemOperationV2025R0,
    HubItemOperationV2025R0ActionField,
)


def refresh_hub_content(
    client: BoxClient, hub_id: str, new_folder_id: str
) -> None:
    """Add a new content folder to the hub."""
    client.hub_items.manage_hub_items_v2025_r0(
        hub_id,
        operations=[
            HubItemOperationV2025R0(
                action=HubItemOperationV2025R0ActionField.ADD,
                item=FolderReferenceV2025R0(id=new_folder_id),
            )
        ],
    )
    print(f"Added folder {new_folder_id} to hub {hub_id}")


def remove_outdated_content(
    client: BoxClient, hub_id: str, old_folder_id: str
) -> None:
    """Remove a folder from the hub."""
    client.hub_items.manage_hub_items_v2025_r0(
        hub_id,
        operations=[
            HubItemOperationV2025R0(
                action=HubItemOperationV2025R0ActionField.REMOVE,
                item=FolderReferenceV2025R0(id=old_folder_id),
            )
        ],
    )
    print(f"Removed folder {old_folder_id} from hub {hub_id}")
