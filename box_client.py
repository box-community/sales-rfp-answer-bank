import os

from dotenv import load_dotenv
from box_sdk_gen import (
    BoxClient,
    BoxCCGAuth,
    CCGConfig,
)

load_dotenv()


def get_box_client() -> BoxClient:
    """Authenticate as a specific Box user via CCG (user_id).

    Requires **Generate User Access Tokens** on the Platform App.
    The client acts with that user's permissions, so the user must have
    access to the Sales Content folders you add to the hub.
    """
    config = CCGConfig(
        client_id=os.getenv("BOX_CLIENT_ID"),
        client_secret=os.getenv("BOX_CLIENT_SECRET"),
        user_id=os.getenv("BOX_USER_ID"),
    )
    auth = BoxCCGAuth(config=config)
    return BoxClient(auth=auth)
