import datetime
import json

import humanize


def show_inbox():
    with open("hinge_creds.json") as f:
        my_user_id = json.load(f)["user_id"]
    with open("conversations.json") as f:
        inbox = json.load(f)
    cur_ts = int(datetime.datetime.now().timestamp() * 1000)
    at_least_one_thread = False
    for channel in inbox["channels"]:
        age = cur_ts - channel["last_message"]["created_at"]
        # Hide conversations older than 30 days
        if age >= 1000 * 86400 * 30:
            continue
        conversant = [m for m in channel["members"] if m["user_id"] != my_user_id][0]
        conversant_name = conversant["nickname"]
        last_message_sender = channel["last_message"]["user"]["nickname"]
        last_message_text = channel["last_message"]["message"]
        is_unread_by_me = (
            channel["last_message"]["created_at"] > channel["read_receipt"][my_user_id]
        )
        is_unread_by_them = (
            channel["last_message"]["created_at"]
            > channel["read_receipt"][conversant["user_id"]]
        )
        print()
        if is_unread_by_me:
            print("  ** NEW MESSAGE **")
        if is_unread_by_them:
            print("  (not yet seen)")
        print(
            f"[ Chat with {conversant_name.upper()} ] :: active {humanize.naturaltime(age / 1000)}"
        )
        print(f"{last_message_sender}: {last_message_text}")
        at_least_one_thread = True
    if at_least_one_thread:
        print()
    else:
        print("(no recent messages)")
