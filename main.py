from fastapi import FastAPI, HTTPException  # ✅ this line is crucial
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://framer.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

@app.get("/")
def root():
    return {"message": "API is running. Use /businesses to get data."}

@app.get("/businesses")
def get_businesses():
    if not (AIRTABLE_BASE_ID and AIRTABLE_TABLE_NAME and AIRTABLE_API_KEY):
        raise HTTPException(status_code=500, detail="Missing Airtable configuration")

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Airtable API request failed: {str(e)}")

    data = response.json()

    businesses = []
    for record in data.get("records", []):
        fields = record.get("fields", {})
        businesses.append({
            "id": record.get("id"),
            "name": fields.get("Name"),
            "category": fields.get("Category"),
            "address": fields.get("Address"),
            "phone": fields.get("Phone"),
        })

    return {"businesses": businesses}
