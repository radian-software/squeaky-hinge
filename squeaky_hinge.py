#!/usr/bin/env python3

import datetime
import json
import urllib.parse

import requests
import websocket

from squeaky_hinge_secrets import *

sendbird_application_id = "3CDAD91C-1E0D-4A0D-BBEE-9671988BF9E9"
hinge_app_version = "9.2.1"
hinge_device_platform = "android"
system_user_agent = "Jand/3.1.12"
sendbird_user_agent = "Android/c3.1.12"
sendbird_device_info = f"Android, 32, 3.1.12, {sendbird_application_id}"

# resp = requests.post(
#     "https://prod-api.hingeaws.net/auth/sms",
#     headers={
#         "X-App-Version": hinge_app_version,
#         "X-Device-Platform": hinge_device_platform,
#     },
#     json={
#         "installId": hinge_install_id,
#         "token": sms_jwt,
#     },
# )

# if not resp.ok:
#     raise Exception(
#         f"got response code {resp.status_code} when fetching Hinge API token"
#     )

# hinge_token_data = resp.json()
# hinge_token = hinge_token_data["token"]
# user_id = hinge_token_data["identityId"]

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
        "User-Agent": system_user_agent,
        "Sb-User-Agent": sendbird_user_agent,
        "Sendbird": sendbird_device_info,
        "Request-Sent-Timestamp": str(int(datetime.datetime.now().timestamp())),
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
    raise Exception(f"got response code {resp.status_code} when fetching conversations")

conversations = resp.json()

print([member["nickname"] for member in conversations["channels"][0]["members"]])
