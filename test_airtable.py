# test_airtable.py
import os
from dotenv import load_dotenv
import requests

load_dotenv()

AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

def test_airtable_fetch():
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch: {response.status_code}, {response.text}")
        return

    data = response.json()
    for record in data.get("records", []):
        fields = record.get("fields", {})
        print(f"- {fields.get('Name')} | {fields.get('Category')} | {fields.get('Address')} | {fields.get('Phone')}")

test_airtable_fetch()
