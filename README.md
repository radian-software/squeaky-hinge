# Squeaky Hinge

> "The squeaky Hinge gets the match"

A well-known issue (to me) with the dating app
[Hinge](https://hinge.co/) is that it sometimes fails to send both
push and email notifications on Android. This applies to both direct
messages as well as new matches. I have already spoken to Hinge's
support team about this and they declined to provide any information
about why this might be, or any assurance that it would be fixed. So,
because I got tired of accidentally ghosting people because I didn't
see their messages, I took matters into my own hands and
reverse-engineered the mobile API to set up actual reliable
notifications for messages.

**Table of contents**

<!-- toc -->

- [Usage](#usage)
- [Configure notifications](#configure-notifications)
- [Set up automatic running and monitoring](#set-up-automatic-running-and-monitoring)
- [Future work](#future-work)

<!-- tocstop -->

## Usage

This is a standard [Poetry](https://python-poetry.org/) project and
can be installed as such or run from source. The entry point is
`./squeaky_hinge.py`:

```
% poetry run ./squeaky_hinge.py --help
usage: squeaky_hinge.py [-h] {login,fetch,inbox,notify} ...

positional arguments:
  {login,fetch,inbox,notify}

options:
  -h, --help            show this help message and exit
```

The subcommands are as follows:

* `login `: Provide your phone number as a positional argument (e.g.
  `+15555555555`). The CLI will run a local server and pop open your
  browser for you to solve a reCAPTCHA which is then used to get
  Google to send an SMS verification code to your phone number, which
  you then have to type in at the command line. The long-lasting API
  credentials are stored in `hinge_creds.json`. You should only have
  to do this once.
* `fetch`: Using the saved API credentials in `hinge_creds.json`,
  fetch your messages and store them in `conversations.json`.
* `inbox`: Display your most recent messages from the data in
  `conversations.json`, using a human-readable format.
* `notify`: Check the data in `conversations.json` and send
  notifications if applicable. This requires configuration (see below)
  to tell how notifications will be sent. If notifications are sent,
  then this will save the timestamp in `last_notified_timestamp.json`
  so that if you run again, you will not get more notifications unless
  there are more recent messages. You can pass the `-n` option to just
  say whether notifications would be sent (dry run), or the `-t`
  option to invoke your notification config with test values to see if
  it works.

You should be able to run all of these subcommands except `notify`
without further configuration. Here is an example session with
placeholder values for personal information:

```
% poetry run ./squeaky_hinge.py login +15555555555
 * Serving Flask app 'recaptcha'
 * Debug mode: off
SMS code from +15555555555: 123456
Successfully (re-)authenticated

% poetry run ./squeaky_hinge.py fetch
Successfully fetched conversations

% poetry run ./squeaky_hinge.py inbox

[ Chat with NAME ] :: active 7 days ago
Radon: The last message I wrote in this conversation

% poetry run ./squeaky_hinge.py notify
No notifications to send
```

## Configure notifications

If you want to use the `notify` subcommand then you should add a file
`squeaky_hinge_notifications.py` which should define a function called
`send_notifications`. This function receives a single argument which
is a list of notifications, like this:

```json
[
  {
    "sender": "Example Sender",
    "text": "Example Message",
    "timestamp": 1661107997231
  },
  {
    "sender": "Another Example Sender",
    "text": "Another Example Message",
    "timestamp": 1661021597231
  }
]
```

If there are no notifications to be sent then your function is not
called, so when it is called, you know there is at least one element
in the list.

From here you can do whatever you want, e.g. display popup using
[terminal-notifier](https://github.com/julienXX/terminal-notifier) or
[Zenity](https://help.gnome.org/users/zenity/stable/), send email
notification via SMTP or SendGrid, send SMS via Twilio, shoot
confetti, etc.

Once you write your notification script, try `./squeaky_hinge.py
notify -t` to test it on some sample data.

## Set up automatic running and monitoring

Of course, to use this script to get notifications, you would want to
run it repeatedly on an automatic schedule. I personally would
recommend setting up a wrapper bash script, something like this:

```bash
#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/squeaky_hinge.bash"

cd "${HOME}/path/to/squeaky_hinge"

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    exec poetry run "${SCRIPT_PATH}" "$@"
fi

if [[ -f "${SCRIPT_DIR}/squeaky_hinge.pid" ]] && (pstree -p "$(<"${SCRIPT_DIR}/squeaky_hinge.pid")" -a | grep squeaky_hinge); then
    echo >&2 "aborting as concurrent process is already running"
    exit 1
else
    echo "$$" >"${SCRIPT_DIR}/squeaky_hinge.pid"
fi

if ! diff -q "poetry.lock" "${VIRTUAL_ENV}/poetry.lock" &>/dev/null; then
    poetry install
    cp "poetry.lock" "${VIRTUAL_ENV}/poetry.lock"
fi

function hinge {
    ./squeaky_hinge.py "$@"
}

hinge fetch
hinge inbox
hinge notify

# setup free account at https://healthchecks.io/ to get notified when
# your script starts failing due to bad auth or upstream api changes, etc
curl https://hc-ping.com/some-url
```

Then you can execute this script in the context of your user account
via crontab or systemd timer, to taste.

## Implementation

This script is based on the Android app for Hinge, because they do not
offer a web interface. To gather the data, I rooted my phone to
install an [mitmproxy](https://mitmproxy.org/) CA in the system trust
store and inspect the requests and responses made during login and
messaging flows. Hinge has a relatively simple API, owing especially
to the fact that they use third-party vendors for both authentication
(Google Identity Platform) and messaging (SendBird). The flow looks
like this:

* Generate a uuid to represent this installation of Hinge, post it to
  `https://prod-api.hingeaws.net/identity/install`
* Use the Firebase web API key that is hardcoded in the Hinge APK to
  get a reCAPTCHA config from Google Identity Platform
  ([docs](https://cloud.google.com/identity-platform/docs/reference/rest/v1/TopLevel/getRecaptchaParams))
* Pop a browser for the user with that reCAPTCHA config to get a
  reCAPTCHA token, this is needed for verification requests if you
  cannot provide the `X-Goog-Spatula` header that comes out of
  proprietary Android code ([more on that
  here](https://gist.github.com/Romern/e58e634e4d70b2be5b57d7abdb77f7ef))
* Exchange user phone number and reCAPTCHA token in the
  [sendVerificationCode
  endpoint](https://cloud.google.com/identity-platform/docs/reference/rest/v1/accounts/sendVerificationCode)
  for some session info
* Get the user to type in the verification code they received to that
  phone number
* Pass session info and verification code to the `verifyPhoneNumber`
  endpoint (which seems to not be publicly documented, only supported
  in [some client
  libraries](https://firebase.google.com/docs/auth/android/phone-auth))
  and get a JWT representing the SMS verification
* Exchange the SMS JWT for a Hinge API key at
  `https://prod-api.hingeaws.net/auth/sms`
* Exchange the Hinge API key for a SendBird access token at
  `https://prod-api.hingeaws.net/message/authenticate`
* Open a websocket connection to the Hinge-specific SendBird API
  endpoint and receive a message containing a session key (more on
  [access token vs session
  key](https://sendbird.com/docs/chat/v3/platform-api/user/creating-users/create-a-user))
* Use the [my\_group\_channels
  endpoint](https://sendbird.com/docs/chat/v3/platform-api/user/managing-joined-group-channels/list-group-channels)
  to get information about conversations in the messaging inbox

## Future work

This script only covers notifications about new messages so far, it
should also ideally be extended to support notifications about new
matches. I think this should be straightforward and will not require
any novel techniques, but I haven't done it yet.

Significant additional work could make build this into a full-featured
open-source Hinge client. It's unlikely that I will take on a project
like that because I don't need it and I'd prefer to avoid getting on
the radar of more corporate lawyers than I need to.
