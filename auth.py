import json
import urllib.parse
import uuid

import requests
import websocket

from squeaky_hinge_config import *

import recaptcha


def authenticate(phone_number):

    hinge_install_id = str(uuid.uuid4()).lower()

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

    if not resp.ok:
        raise Exception(
            f"got response code {resp.status_code} when getting ReCAPTCHA parameters"
        )

    recaptcha_params = resp.json()
    recaptcha_site_key = recaptcha_params["recaptchaSiteKey"]
    recaptcha_token = recaptcha.get_token(recaptcha_site_key)

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

    if not resp.ok:
        raise Exception(f"got response code {resp.status_code} when sending SMS code")

    sms_send_info = resp.json()
    session_info = sms_send_info["sessionInfo"]

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

    if not resp.ok:
        raise Exception(f"got response code {resp.status_code} when verifying SMS code")

    sms_verify_info = resp.json()
    sms_jwt = sms_verify_info["access_token"]

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

    if not resp.ok:
        raise Exception(
            f"got response code {resp.status_code} when fetching Hinge API token"
        )

    hinge_token_data = resp.json()
    hinge_token = hinge_token_data["token"]
    user_id = hinge_token_data["identityId"]

    with open("hinge-creds.json", "w") as f:
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
