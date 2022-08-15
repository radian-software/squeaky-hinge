#!/usr/bin/env python3

import argparse

import auth
import conversations


def do_login(args):
    auth.authenticate(args.phone_number)
    print("Successfully (re-)authenticated")


def do_inbox(args):
    inbox = conversations.get_conversations()
    print([member["nickname"] for member in inbox["channels"][0]["members"]])


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
subparsers.required = True
subparser_login = subparsers.add_parser("login")
subparser_login.set_defaults(func=do_login)
subparser_login.add_argument("phone_number", type=str)
subparser_inbox = subparsers.add_parser("inbox")
subparser_inbox.set_defaults(func=do_inbox)

args = parser.parse_args()
args.func(args)
