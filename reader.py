import datetime
import json
import logging

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


def send_notifications(args):
    logging.info(f"START notification flow")

    from squeaky_hinge_notifications import send_notifications

    if args.dry_run:

        def func(notifications):
            print(
                f"Would send notifications about following {len(notifications)} message(s):"
            )
            print(json.dumps(notifications, indent=2))

        send_notifications_wrapped = func

    else:

        def func(notifications):
            send_notifications(notifications)
            new_last_notified_ts = max(n["timestamp"] for n in notifications)
            logging.info(f"Updating last notified timestamp to {new_last_notified_ts}")
            with open("last_notified_timestamp.json", "w") as f:
                json.dump(
                    {"last_notified_timestamp": new_last_notified_ts}, f, indent=2
                )
                f.write("\n")

        send_notifications_wrapped = func

    with open("hinge_creds.json") as f:
        my_user_id = json.load(f)["user_id"]
    with open("conversations.json") as f:
        inbox = json.load(f)
    cur_ts = int(datetime.datetime.now().timestamp() * 1000)
    try:
        with open("last_notified_timestamp.json") as f:
            last_notified_timestamp = json.load(f)["last_notified_timestamp"]
    except FileNotFoundError:
        # If file not found, assume we have never notified before.
        last_notified_timestamp = 0
    notifications = []
    for idx, channel in enumerate(inbox["channels"]):
        age = cur_ts - channel["last_message"]["created_at"]
        # Ignore conversations older than 30 days
        if age >= 1000 * 86400 * 30:
            continue
        logging.info(
            f'For conversation #{idx}: last message at {channel["last_message"]["created_at"]}, my read receipt at {channel["read_receipt"][my_user_id]}, last notification timestamp at {last_notified_timestamp}'
        )
        if channel["last_message"]["created_at"] > max(
            channel["read_receipt"][my_user_id], last_notified_timestamp
        ):
            notifications.append(
                {
                    "sender": channel["last_message"]["user"]["nickname"],
                    "text": channel["last_message"]["text"],
                    "timestamp": channel["last_message"]["created_at"],
                }
            )
    logging.info(f"Produced notification list: {json.dumps(notifications)}")
    if not notifications:
        print("No notifications to send")
        return
    send_notifications_wrapped(notifications)

    logging.info(f"SUCCESS notification flow")


def test_notifications(args):
    from squeaky_hinge_notifications import send_notifications

    cur_ts = int(datetime.datetime.now().timestamp() * 1000) - (1000 * 3600)

    send_notifications(
        [
            {
                "sender": "Example Sender",
                "text": "Example Message",
                "timestamp": cur_ts,
            },
            {
                "sender": "Another Example Sender",
                "text": "Another Example Message",
                "timestamp": cur_ts - (1000 * 3600 * 24),
            },
        ]
    )
