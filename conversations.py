import json
import logging
import urllib.parse

import requests
import websocket

from squeaky_hinge_config import *


def fetch_conversations():
    logging.info(f"START inbox flow")

    with open("hinge_creds.json") as f:
        data = json.load(f)

    hinge_token = data["hinge_token"]
    user_id = data["user_id"]
    hinge_install_id = data["hinge_install_id"]
    logging.info(f"Using Hinge token {hinge_token}")
    logging.info(f"Using user ID {user_id}")
    logging.info(f"Using Hinge install ID {hinge_install_id}")

    logging.info(f"Using X-App-Version {hinge_android_package}")
    logging.info(f"Using X-Device-Platform {hinge_apk_sha1sum}")
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
    logging.info(
        f"Invoked message/authenticate and got response code {resp.status_code} and body: {resp.text}"
    )

    if not resp.ok:
        raise Exception(
            f"got response code {resp.status_code} when fetching Sendbird access token"
        )

    sendbird_auth_data = resp.json()
    sendbird_access_token = sendbird_auth_data["token"]
    logging.info(f"Got SendBird access token {sendbird_access_token}")

    logging.info(f"Using SendBird application ID {sendbird_application_id}")
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

    sendbird_ws_message = ws.recv()
    logging.info(f"Opened SendBird websocket and got message {sendbird_ws_message}")
    sendbird_ws_data = json.loads(sendbird_ws_message.removeprefix("LOGI"))

    sendbird_session_key = sendbird_ws_data["key"]
    logging.info(f"Got SendBird session key {sendbird_session_key}")

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
    logging.info(
        f"Invoked my_group_channels and got response code {resp.status_code} and body: {resp.text}"
    )

    if not resp.ok:
        raise Exception(
            f"got response code {resp.status_code} when fetching conversations"
        )

    conversations = resp.json()

    with open("conversations.json", "w") as f:
        json.dump(conversations, f, indent=2)
        f.write("\n")

    logging.info(f"SUCCESS inbox flow")
