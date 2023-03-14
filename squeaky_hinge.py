#!/usr/bin/env python3

import argparse
import logging

import auth
import conversations
import reader


logging.basicConfig(
    filename="hinge.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)


def do_login(args):
    auth.authenticate(args.phone_number)
    print("Successfully (re-)authenticated")


def do_fetch(args):
    conversations.fetch_conversations(include_messages=False)
    print("Successfully fetched conversations")


def do_messages(args):
    conversations.fetch_conversations(include_messages=True)
    print("Successfully fetched conversations and messages")


def do_inbox(args):
    reader.show_inbox()


def do_notify(args):
    if args.test:
        reader.test_notifications(args)
    else:
        reader.send_notifications(args)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
subparsers.required = True
subparser_login = subparsers.add_parser("login")
subparser_login.set_defaults(func=do_login)
subparser_login.add_argument("phone_number", type=str)
subparser_fetch = subparsers.add_parser("fetch")
subparser_fetch.set_defaults(func=do_fetch)
subparser_fetch = subparsers.add_parser("messages")
subparser_fetch.set_defaults(func=do_messages)
subparser_inbox = subparsers.add_parser("inbox")
subparser_inbox.set_defaults(func=do_inbox)
subparser_notify = subparsers.add_parser("notify")
subparser_notify.set_defaults(func=do_notify)
subparser_notify.add_argument("-n", "--dry-run", action="store_true")
subparser_notify.add_argument("-t", "--test", action="store_true")
subparser_notify.add_argument("-k", "--keep-unread", action="store_true")
subparser_notify.add_argument("-r", "--mark-read", action="store_true")

args = parser.parse_args()
args.func(args)
