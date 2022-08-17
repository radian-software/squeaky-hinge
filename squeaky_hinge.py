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
    conversations.fetch_conversations()
    print("Successfully fetched conversations")


def do_inbox(args):
    reader.show_inbox()


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
subparsers.required = True
subparser_login = subparsers.add_parser("login")
subparser_login.set_defaults(func=do_login)
subparser_login.add_argument("phone_number", type=str)
subparser_fetch = subparsers.add_parser("fetch")
subparser_fetch.set_defaults(func=do_fetch)
subparser_inbox = subparsers.add_parser("inbox")
subparser_inbox.set_defaults(func=do_inbox)

args = parser.parse_args()
args.func(args)
