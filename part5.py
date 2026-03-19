"""
Operation Ditwah – Part 5: News Feed Extraction Pipeline
========================================================
Extracts structured JSON from unstructured raw text feeds
using Pydantic models. Converts the objects to a Pandas dataframe
and exports an Excel tracking report.
"""

import os
import json
import time
import pandas as pd
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── 1. PYDANTIC SCHEMA ────────────────────────────────────────────────────────
class CrisisEvent(BaseModel):
    district: str = Field(description="The district mentioned, or 'Unknown'")
    flood_level_meters: float = Field(description="Estimated flood level in meters if mentioned. Use 0.0 if not mentioned.")
    victim_count: int = Field(description="Number of people trapped, injured, or needing help. Use 0 if not mentioned.")
    main_need: str = Field(description="The primary thing requested (e.g. 'Boat', 'Rations', 'Helicopter'). Use 'None' if none.")
    status: str = Field(description="Either 'Critical', 'Warning', 'Safe', or 'Info'")

# ── 2. JSON EXTRACTION SETUP ──────────────────────────────────────────────────
JSON_EXTRACT_PROMPT = """
Analyze the following news feed item.
Extract the details into the required JSON schema.

Feed item:
{item}
"""

def extract_json(item_text: str) -> CrisisEvent | None:
    """Force Gemini to output JSON matching our Pydantic schema."""
    prompt = JSON_EXTRACT_PROMPT.format(item=item_text)
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                # The GenAI SDK supports passing the Pydantic class directly to response_schema
                response_schema=CrisisEvent,
            ),
        )
        
        # Parse output JSON into our Pydantic Object
        json_str = response.text.strip()
        
        # Pydantic validation guarantees the types are correct
        event = CrisisEvent.model_validate_json(json_str)
        return event

    except Exception as e:
        print(f"⚠️ Extraction failed for item: {item_text[:30]}... Error: {e}")
        return None

# ── 3. PIPELINE EXECUTION ─────────────────────────────────────────────────────
def main():
    print("==========================================================")
    print(" PART 5: NEWS FEED EXTRACTION PIPELINE (PYDANTIC)         ")
    print("==========================================================\n")
    
    # 1. Load the feed
    with open("data/News Feed.txt", "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip()]
        
    print(f"📂 Loaded {len(items)} items from News Feed.txt")
    
    # 2. Extract Data
    extracted_events = []
    
    for i, item in enumerate(items, 1):
        print(f"[{i:02d}/{len(items)}] Extracting: {item[:50]}...")
        
        event = extract_json(item)
        if event:
             extracted_events.append(event.model_dump())
             
        time.sleep(1) # Rate limit protection

    # 3. Export to Pandas/Excel
    if extracted_events:
        os.makedirs("output", exist_ok=True)
        df = pd.DataFrame(extracted_events)
        output_path = "output/flood_report.xlsx"
        df.to_excel(output_path, index=False)
        
        print(f"\n✅ Done! Extracted {len(extracted_events)} valid entries.")
        print(f"📊 Report saved to: {output_path}")
        print("\n--- SAMPLE OUTPUT DATA ---")
        print(df.head())
    else:
        print("\n❌ No valid data extracted.")

if __name__ == "__main__":
    main()
