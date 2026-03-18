"""
Operation Ditwah – Part 1: Few-Shot Message Classifier
======================================================
Classifies disaster messages using few-shot prompting with Gemini.
Output: output/classified_messages.xlsx
"""

import os
import re
import time
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ── 1. SETUP ──────────────────────────────────────────────────────────────────
load_dotenv()  # Load GEMINI_API_KEY from .env file
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── 2. FEW-SHOT PROMPT ────────────────────────────────────────────────────────
# This is the "contract" we teach Gemini by showing labelled examples.
# The model learns the pattern from examples, then applies it to new messages.

FEW_SHOT_PROMPT = """
You are a disaster relief triage assistant for Sri Lanka.
Your job is to classify incoming messages from the public during a cyclone emergency.

CATEGORIES:
- Rescue  → Someone needs physical rescue (trapped, stranded, life threat)
- Supply  → Someone needs food, water, medicine, or other supplies
- Info    → A news update, status report, or general information (not urgent)
- Other   → Irrelevant, spam, or cannot be acted upon

DISTRICTS: Colombo, Gampaha, Kandy, Kalutara, Galle, Matara, Ratnapura, Kegalle, Nuwara Eliya
If no district is clearly mentioned, write None.

PRIORITY: High (immediate action needed) or Low (no urgency)

OUTPUT FORMAT (strictly one line, NO extra text):
District: [Name or None] | Intent: [Category] | Priority: [High/Low]

---

HERE ARE EXAMPLES TO LEARN FROM:

Message: "BREAKING: Water levels in Kelani River (Colombo) have reached 9.5 meters. Critical flood warning issued."
District: Colombo | Intent: Info | Priority: Low

Message: "SOS: 5 people trapped on a roof in Ja-Ela (Gampaha). Water rising fast. Need boat immediately."
District: Gampaha | Intent: Rescue | Priority: High

Message: "We need milk powder for 10 babies at the temple camp."
District: None | Intent: Supply | Priority: High

Message: "Colombo Fort station is dry. Trains are running on schedule."
District: Colombo | Intent: Info | Priority: Low

Message: "URGENT: Landslide in Badulla. 2 houses buried. Need rescue team."
District: None | Intent: Rescue | Priority: High

Message: "Just arrived in Galle. Weather is nice."
District: Galle | Intent: Other | Priority: Low

Message: "Gampaha hospital is requesting drinking water for patients."
District: Gampaha | Intent: Supply | Priority: High

Message: "Please pray for Sri Lanka."
District: None | Intent: Other | Priority: Low

---

Now classify this message. Reply with ONLY the output line, nothing else:

Message: "{message}"
"""

# ── 3. LOAD MESSAGES ──────────────────────────────────────────────────────────
def load_messages(filepath: str) -> list[str]:
    """Read the text file and split into individual messages (separated by blank lines)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split on one or more blank lines, strip whitespace, remove empties
    messages = [msg.strip() for msg in content.split("\n\n") if msg.strip()]
    print(f"✅ Loaded {len(messages)} messages from {filepath}\n")
    return messages


# ── 4. CLASSIFY A SINGLE MESSAGE ──────────────────────────────────────────────
def classify_message(message: str) -> dict:
    """Send one message to Gemini using the few-shot prompt and parse the result."""
    prompt = FEW_SHOT_PROMPT.format(message=message)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.0),
        )
        raw = response.text.strip()

        # Parse structured output: "District: X | Intent: Y | Priority: Z"
        district_match = re.search(r"District:\s*([^|]+)", raw)
        intent_match   = re.search(r"Intent:\s*([^|]+)", raw)
        priority_match = re.search(r"Priority:\s*(\w+)", raw)

        district = district_match.group(1).strip() if district_match else "Unknown"
        intent   = intent_match.group(1).strip()   if intent_match   else "Unknown"
        priority = priority_match.group(1).strip()  if priority_match else "Unknown"

    except Exception as e:
        print(f"  ⚠️  API error: {e}")
        district, intent, priority, raw = "Error", "Error", "Error", str(e)

    return {
        "Message":  message,
        "District": district,
        "Intent":   intent,
        "Priority": priority,
        "Raw Output": raw,
    }


# ── 5. MAIN PIPELINE ──────────────────────────────────────────────────────────
def main():
    # Load all messages
    messages = load_messages("data/Sample Messages.txt")

    results = []
    for i, msg in enumerate(messages, 1):
        print(f"[{i:02d}/{len(messages)}] Classifying: \"{msg[:60]}...\"" if len(msg) > 60 else f"[{i:02d}/{len(messages)}] Classifying: \"{msg}\"")

        result = classify_message(msg)
        results.append(result)

        print(f"         → District: {result['District']} | Intent: {result['Intent']} | Priority: {result['Priority']}")

        # Small delay to stay within free-tier rate limits (15 req/min)
        time.sleep(1)

    # ── 6. SAVE TO EXCEL ──────────────────────────────────────────────────────
    os.makedirs("output", exist_ok=True)
    df = pd.DataFrame(results)
    output_path = "output/classified_messages.xlsx"
    df.to_excel(output_path, index=False)

    print(f"\n✅ Done! Results saved to: {output_path}")
    print(f"   Total classified: {len(results)} messages")

    # ── 7. QUICK SUMMARY ──────────────────────────────────────────────────────
    print("\n📊 Classification Summary:")
    print(df["Intent"].value_counts().to_string())
    print("\n🚨 High Priority Messages:")
    high = df[df["Priority"] == "High"][["Message", "Intent"]]
    for _, row in high.iterrows():
        print(f"  [{row['Intent']}] {row['Message'][:80]}")


if __name__ == "__main__":
    main()
