"""
Operation Ditwah – Part 3: The Logistics Commander (CoT & ToT)
==============================================================
Scores triage incidents logically using Chain-of-Thought, then uses
Tree-of-Thoughts style search to explore routing paths and choose
the optimal rescue logistics strategy.
"""

import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

COT_SCORING_PROMPT = """
You are prioritizing emergency incidents.
Review the incident details.

Calculate a Priority Score from 1 to 10 based on:
- Age (Very young or elderly -> higher risk)
- Main Need: If "Rescue" add +3. If "Insulin" or "Medicine" add +1.
- Urgency: Imminent life threat?

Provide your thinking (Step 1: Age analysis, Step 2: Need analysis, Step 3: Urgency).
CONCLUDE with exactly this format on the last line:
SCORE: X
Where X is an integer from 1 to 10.

Incident Details:
{incident}
"""

def get_cot_score(incident_text: str) -> int:
    """Use Gemini to calculate a CoT score for the incident."""
    prompt = COT_SCORING_PROMPT.format(incident=incident_text)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.0),
    )
    
    text = response.text.strip()
    print(f"\n🧠 [CoT Reasoning for: {incident_text.split('|')[2].strip()}]")
    print(text)
    
    # Extract the score using regex
    match = re.search(r"SCORE:\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return int(text.split()[-1]) if text.split()[-1].isdigit() else 5

def main():
    print("==========================================================")
    print(" PART 3: THE LOGISTICS COMMANDER (CoT & ToT)              ")
    print("==========================================================\n")
    
    # 1. READ INCIDENTS
    lines = []
    with open("data/Incidents.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("ID")]
        
    incidents = []
    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 6:
            location = parts[2]
            # CoT Step: Let model evaluate the score based on the raw text
            score = get_cot_score(line)
            incidents.append({
                "location": location,
                "text": line,
                "score": score
            })

    print("\n\n📍 --- SCORED INCIDENTS ---")
    for inc in incidents:
        print(f"Location: {inc['location']:<10} | Priority Score: {inc['score']:<2} | Info: {inc['text'][:40]}...")

    # 2. ToT ROUTING (Tree of Thoughts)
    # Travel Times: Ragama -> Ja-Ela (10m), Ja-Ela -> Gampaha (40m).
    # Boat starts at: Ragama.
    book = {inc["location"]: inc["score"] for inc in incidents}
    
    ragama_score = book.get("Ragama", 0)
    jaela_score = book.get("Ja-Ela", 0)
    gampaha_score = book.get("Gampaha", 0)

    print("\n\n🗺️ --- ToT ROUTE EXPLORATION ---")
    
    # Route 1: Highest Score First
    sorted_locs = sorted(incidents, key=lambda x: x["score"], reverse=True)
    highest_route = [x["location"] for x in sorted_locs]
    # Calculate travel time for Highest Score First route
    time_hsf = 0
    current_loc = "Ragama" # Boat is at Ragama
    distances = {
        ("Ragama", "Ja-Ela"): 10, ("Ja-Ela", "Ragama"): 10,
        ("Ja-Ela", "Gampaha"): 40, ("Gampaha", "Ja-Ela"): 40,
        ("Ragama", "Gampaha"): 50, ("Gampaha", "Ragama"): 50 # 10 + 40
    }
    
    for dest in highest_route:
        if dest != current_loc:
            time_hsf += distances.get((current_loc, dest), 0)
            current_loc = dest
    
    # Route 2: Closest First (Ragama -> Ja-Ela -> Gampaha)
    time_closest = 0 + 10 + 40 # 50 mins
    
    # Route 3: Furthest First (Gampaha -> Ja-Ela -> Ragama)
    time_furthest = 50 + 40 + 10 # 100 mins

    print(f"BRANCH 1: Highest Score First -> {highest_route} (Est Time: {time_hsf}m)")
    print(f"BRANCH 2: Closest First       -> ['Ragama', 'Ja-Ela', 'Gampaha'] (Est Time: {time_closest}m)")
    print(f"BRANCH 3: Furthest First      -> ['Gampaha', 'Ja-Ela', 'Ragama'] (Est Time: {time_furthest}m)")
    
    print("\n✅ OPTIMAL ROUTE DECISION:")
    best = min((time_hsf, "Highest Score First"), (time_closest, "Closest First"))
    # In emergency routing, maximizing scores while minimizing delay is key.
    print(f"The commander selects '{best[1]}' because it optimally saves the highest priorities with an efficient {best[0]} min drive time.")

if __name__ == "__main__":
    main()
