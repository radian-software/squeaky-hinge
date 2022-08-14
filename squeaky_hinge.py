#!/usr/bin/env python3

import datetime

import requests

from squeaky_hinge_secrets import *

hinge_app_version = "9.2.1"
hinge_device_platform = "android"
system_user_agent = "Jand/3.1.12"
sendbird_user_agent = "Android/c3.1.12"
sendbird_device_info = f"Android, 32, 3.1.12, {sendbird_device_id}"

resp = requests.get(
    "https://prod-api.hingeaws.net/user/v2",
    headers={
        "Authorization": f"Bearer {hinge_token}",
        "X-App-Version": hinge_app_version,
        "X-Device-Platform": hinge_device_platform,
        "X-Install-Id": hinge_install_id,
    },
)

if not resp.ok:
    raise Exception(f"got response code {resp.status_code} when fetching user profile")

user_profile = resp.json()
user_id = user_profile["identityId"]

resp = requests.get(
    f"https://api-hinge.sendbird.com/v3/users/{user_id}/my_group_channels",
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
