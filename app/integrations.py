"""Pluggable enrichment + email-sending adapters.

These only activate if you supply the relevant API key / SMTP credentials in
.env. Without keys, the app still works fully for manually-entered and
CSV-imported leads.
"""
import os
import smtplib
from email.mime.text import MIMEText

import requests

APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY")
APOLLO_SEARCH_URL = "https://api.apollo.io/v1/mixed_companies/search"

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "")


class ApolloNotConfigured(Exception):
    pass


def apollo_search_companies(keywords, locations=None, per_page=25):
    """Search Apollo.io for companies by industry keyword (e.g. 'food and beverage manufacturer').

    Requires APOLLO_API_KEY. Returns a list of dicts with name/website/industry/location.
    """
    if not APOLLO_API_KEY:
        raise ApolloNotConfigured(
            "Set APOLLO_API_KEY in your .env to enable prospect search via Apollo.io."
        )

    payload = {
        "api_key": APOLLO_API_KEY,
        "q_organization_keyword_tags": [keywords],
        "page": 1,
        "per_page": per_page,
    }
    if locations:
        payload["organization_locations"] = [locations]

    resp = requests.post(APOLLO_SEARCH_URL, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for org in data.get("organizations", []) + data.get("accounts", []):
        results.append(
            {
                "name": org.get("name"),
                "website": org.get("website_url"),
                "city": org.get("city"),
                "state": org.get("state"),
                "employee_count": org.get("estimated_num_employees"),
            }
        )
    return results


class SmtpNotConfigured(Exception):
    pass


def send_email(to_address, subject, body):
    if not (SMTP_USERNAME and SMTP_PASSWORD):
        raise SmtpNotConfigured(
            "Set SMTP_USERNAME and SMTP_PASSWORD (Gmail app password) in your .env to send email."
        )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USERNAME}>" if SMTP_FROM_NAME else SMTP_USERNAME
    msg["To"] = to_address

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, [to_address], msg.as_string())
