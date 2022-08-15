import json
import logging
import urllib.parse
import uuid

import requests
import websocket

from squeaky_hinge_config import *

import recaptcha


def authenticate(phone_number):
    logging.info(f"START authentication flow")

    hinge_install_id = str(uuid.uuid4()).lower()
    logging.info(f"Generated new Hinge install ID {hinge_install_id}")

    logging.info(f"Using X-Android-Package {hinge_android_package}")
    logging.info(f"Using X-Android-Cert {hinge_apk_sha1sum}")
    logging.info(f"Using Firebase web API key {firebase_web_api_key}")
    resp = requests.get(
        "https://identitytoolkit.googleapis.com/v1/recaptchaParams",
        headers={
            "X-Android-Package": hinge_android_package,
            "X-Android-Cert": hinge_apk_sha1sum,
        },
        params={
            "alt": "json",
            "key": firebase_web_api_key,
        },
    )
    logging.info(
        f"Invoked recaptchaParams and got response code {resp.status_code} and body: {resp.text}"
    )

    if not resp.ok:
        raise Exception(
            f"got response code {resp.status_code} when getting ReCAPTCHA parameters"
        )

    recaptcha_params = resp.json()
    recaptcha_site_key = recaptcha_params["recaptchaSiteKey"]
    logging.info(f"Got reCAPTCHA site key {recaptcha_site_key}")
    recaptcha_token = recaptcha.get_token(recaptcha_site_key)
    logging.info(f"Got reCAPTCHA token {recaptcha_token}")

    logging.info(f"Using phone number {phone_number}")
    resp = requests.post(
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendVerificationCode",
        headers={
            "X-Android-Package": hinge_android_package,
            "X-Android-Cert": hinge_apk_sha1sum,
        },
        json={
            "phone_number": phone_number,
            "recaptcha_token": recaptcha_token,
        },
        params={
            "alt": "json",
            "key": firebase_web_api_key,
        },
    )
    logging.info(
        f"Invoked sendVerificationCode and got response code {resp.status_code} and body: {resp.text}"
    )

    if not resp.ok:
        raise Exception(f"got response code {resp.status_code} when sending SMS code")

    sms_send_info = resp.json()
    session_info = sms_send_info["sessionInfo"]
    logging.info(f"Got session info {session_info}")

    resp = requests.post(
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPhoneNumber",
        headers={
            "X-Android-Package": hinge_android_package,
            "X-Android-Cert": hinge_apk_sha1sum,
        },
        json={
            "sessionInfo": session_info,
            "code": input(f"SMS code from {phone_number}: "),
        },
        params={
            "alt": "json",
            "key": firebase_web_api_key,
        },
    )
    logging.info(
        f"Invoked verifyPhoneNumber and got response code {resp.status_code} and body: {resp.text}"
    )

    if not resp.ok:
        raise Exception(f"got response code {resp.status_code} when verifying SMS code")

    sms_verify_info = resp.json()
    sms_jwt = sms_verify_info["access_token"]
    logging.info(f"Got SMS JWT {sms_jwt}")

    logging.info(f"Using X-App-Version {hinge_android_package}")
    logging.info(f"Using X-Device-Platform {hinge_apk_sha1sum}")
    resp = requests.post(
        "https://prod-api.hingeaws.net/auth/sms",
        headers={
            "X-App-Version": hinge_app_version,
            "X-Device-Platform": hinge_device_platform,
        },
        json={
            "installId": hinge_install_id,
            "token": sms_jwt,
        },
    )
    logging.info(
        f"Invoked auth/sms and got response code {resp.status_code} and body: {resp.text}"
    )

    if not resp.ok:
        raise Exception(
            f"got response code {resp.status_code} when fetching Hinge API token"
        )

    hinge_token_data = resp.json()
    hinge_token = hinge_token_data["token"]
    user_id = hinge_token_data["identityId"]
    logging.info(f"Got Hinge token {hinge_token}")
    logging.info(f"Got user ID {user_id}")

    with open("hinge_creds.json", "w") as f:
        json.dump(
            {
                "hinge_token": hinge_token,
                "user_id": user_id,
                "hinge_install_id": hinge_install_id,
            },
            f,
            indent=2,
        )
        f.write("\n")

    logging.info(f"SUCCESS authentication flow")
