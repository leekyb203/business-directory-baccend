from fastapi import FastAPI
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow Framer to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Optionally restrict to Framer's domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AIRTABLE_API_KEY = "patFmu3Kgn3SY7v7k.fc8f976fdd4a26213789f962be921c1e7799b5909d96f9b100efdd1264be4a9d"
BASE_ID = "appXV0uyIXcxrFkEe"
TABLE_NAME = "Local Businesses"

@app.get("/")
def read_root():
    return {"message": "API Live"}

@app.get("/businesses")
def get_local_businesses():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        records = response.json().get("records", [])
        # Clean response to only return necessary fields
        businesses = []
        for record in records:
            fields = record.get("fields", {})
            businesses.append(fields)
        return {"businesses": businesses}
    else:
        return {"error": "Failed to fetch records", "details": response.text}
