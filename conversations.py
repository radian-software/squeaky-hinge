import json
import urllib.parse

import requests
import websocket

from squeaky_hinge_config import *


def get_conversations():

    with open("hinge-creds.json") as f:
        data = json.load(f)

    hinge_token = data["hinge_token"]
    user_id = data["user_id"]
    hinge_install_id = data["hinge_install_id"]

    resp = requests.post(
        "https://prod-api.hingeaws.net/message/authenticate",
        headers={
            "Authorization": f"Bearer {hinge_token}",
            "X-App-Version": hinge_app_version,
            "X-Device-Platform": hinge_device_platform,
            "X-Install-Id": hinge_install_id,
        },
        json={"refresh": False},
    )

    if not resp.ok:
        raise Exception(
            f"got response code {resp.status_code} when fetching Sendbird access token"
        )

    sendbird_auth_data = resp.json()
    sendbird_access_token = sendbird_auth_data["token"]

    ws = websocket.create_connection(
        f"wss://ws-{sendbird_application_id.lower()}.sendbird.com?"
        + urllib.parse.urlencode(
            {
                "ai": sendbird_application_id,
                "user_id": user_id,
                "access_token": sendbird_access_token,
            }
        ),
    )

    sendbird_ws_data = json.loads(ws.recv().removeprefix("LOGI"))
    sendbird_session_key = sendbird_ws_data["key"]

    resp = requests.get(
        f"https://api-{sendbird_application_id.lower()}.sendbird.com/v3/users/{user_id}/my_group_channels",
        headers={
            "Accept": "application/json",
            "Session-Key": sendbird_session_key,
        },
        params={
            "show_member": "true",
            "show_frozen": "true",
            "public_mode": "all",
            "member_state_filter": "all",
            "hidden_mode": "unhidden_only",
            "show_delivery_receipt": "true",
            "distinct_mode": "all",
            "unread_filter": "all",
            "token": "",
            "show_read_receipt": "true",
            "super_mode": "all",
            "show_metadata": "true",
            "limit": "20",
            "show_empty": "true",
            "order": "latest_last_message",
        },
    )

    if not resp.ok:
        raise Exception(
            f"got response code {resp.status_code} when fetching conversations"
        )

    conversations = resp.json()

    return conversations
