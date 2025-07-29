from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
from typing import Optional

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cherished-reflect-856896.framer.app",
        "https://framer.com",
        "https://preview.framer.com", 
        "https://*.framer.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"  # Remove this in production
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
def get_businesses(
    category: Optional[str] = Query(None),
    borough: Optional[str] = Query(None),
    priceRange: Optional[str] = Query(None),
    rating: Optional[str] = Query(None)
):
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
        
        # Split category: "Barbecue - Food" → category: "Food", subcategory: "Barbecue"
        category_full = fields.get("Category", "")
        if " - " in category_full:
            subcategory, main_category = category_full.split(" - ", 1)
        else:
            main_category = category_full
            subcategory = category_full
        
        # Extract borough from address: "37 Bruckner Blvd, Bronx, NY 10454" → "Bronx"
        address = fields.get("Address", "")
        borough_extracted = ""
        if address:
            address_parts = address.split(", ")
            if len(address_parts) >= 2:
                borough_extracted = address_parts[1]
        
        # Check if business is new (opened within last 30 days)
        is_new = False
        open_date = fields.get("Open Date", "")
        if open_date:
            try:
                # Handle different date formats
                if "T" in open_date:  # ISO format
                    open_dt = datetime.fromisoformat(open_date.replace("Z", "+00:00"))
                else:  # Simple date format
                    open_dt = datetime.strptime(open_date, "%Y-%m-%d")
                thirty_days_ago = datetime.now() - timedelta(days=30)
                is_new = open_dt >= thirty_days_ago
            except:
                is_new = False
        
        # Handle image field (Airtable attachments)
        image_url = ""
        if "Image" in fields and fields["Image"]:
            image_url = fields["Image"][0]["url"]
        else:
            # Default images based on category
            default_images = {
                "Food": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=300&fit=crop",
                "Beauty": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400&h=300&fit=crop",
                "Services": "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=400&h=300&fit=crop",
                "Shopping": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=300&fit=crop",
                "Health": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=400&h=300&fit=crop"
            }
            image_url = default_images.get(main_category, default_images["Food"])
        
        # Build business object in the format frontend expects
        business = {
            "id": record.get("id"),
            "name": fields.get("Business Name", ""),
            "category": main_category,
            "subcategory": subcategory,
            "borough": borough_extracted,
            "rating": fields.get("Rating", 4.0),  # Add this field to Airtable
            "priceRange": fields.get("Price Range", "$$"),  # Add this field to Airtable
            "image": image_url,
            "address": address,
            "phone": fields.get("Phone Number", ""),
            "description": fields.get("Description", ""),
            "isNew": is_new,
            "openDate": open_date
        }
        
        businesses.append(business)
    
    # Apply filters
    filtered_businesses = businesses
    
    if category and category != "All":
        filtered_businesses = [b for b in filtered_businesses if b["category"] == category]
    
    if borough and borough != "All":
        filtered_businesses = [b for b in filtered_businesses if b["borough"] == borough]
    
    if priceRange and priceRange != "All":
        filtered_businesses = [b for b in filtered_businesses if b["priceRange"] == priceRange]
    
    if rating and rating != "All":
        min_rating = float(rating.replace("+", ""))
        filtered_businesses = [b for b in filtered_businesses if b["rating"] >= min_rating]
    
    # ✅ CRITICAL: Return array directly, not wrapped in "businesses" key
    return filtered_businesses

@app.get("/debug-airtable")
def debug_airtable():
    """Debug endpoint to see raw Airtable data"""
    if not (AIRTABLE_BASE_ID and AIRTABLE_TABLE_NAME and AIRTABLE_API_KEY):
        raise HTTPException(status_code=500, detail="Missing Airtable configuration")

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Airtable API request failed: {str(e)}")