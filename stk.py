import os
import base64
import requests
from datetime import datetime

CONSUMER_KEY = os.getenv("zhwFg9gbNCyAfTRiG86jeU1GRCohH4wCVEBTdJl2vEjMOpMU")
CONSUMER_SECRET = os.getenv("fAzDwJjXBFBbaVtS0GDR1kAZceGPPNxH0rkKxouHgPVGimdOkCo2Eu22RoUmay3m")

SHORTCODE = "174379"

PASSKEY = "YOUR_SANDBOX_PASSKEY"

CALLBACK_URL = os.getenv("CALLBACK_URL")

TOKEN_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

STK_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"


def get_access_token():

    response = requests.get(
        TOKEN_URL,
        auth=(CONSUMER_KEY, CONSUMER_SECRET)
    )

    return response.json()["access_token"]


def stk_push(phone, amount, account_reference, description):

    token = get_access_token()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password = base64.b64encode(
        (SHORTCODE + PASSKEY + timestamp).encode()
    ).decode()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": description
    }

    response = requests.post(
        STK_URL,
        json=payload,
        headers=headers
    )

    return response.json()
