from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cherished-reflect-856896.framer.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AIRTABLE_API_KEY = "patFmu3Kgn3SY7v7k.80c40ba03d4d1820cdd0b830dd30a958a4559b5d9f1b4ea552322b4d9b1885a7"
BASE_ID = "appXV0uyIXcxrFkEe"
TABLE_NAME = "Businesses"

@app.get("/")
def read_root():
    return {"message": "API Live"}

@app.get("/api/businesses")
def get_businesses():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
