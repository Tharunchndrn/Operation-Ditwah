"""
Operation Ditwah – Part 4: The Budget Keeper (Token Economics)
==============================================================
Demonstrates token limits and cost control.
Calculates token usage of incoming messages and aggressively
summarizes or truncates them if they exceed 150 tokens.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── PROMPTS ───────────────────────────────────────────────────────────────────
OVERFLOW_SUMMARIZE_PROMPT = """
The following message is too long and exceeds our token budget.
Extract ONLY the core actionable emergency details.
Discard greetings, prayers, random news, and irrelevant context.
Limit your response to 1 brief sentence.

Message:
{message}
"""

def process_message(message: str) -> str:
    """Check token count and either pass or summarize the message."""
    print(f"\n📨 INCOMING MESSAGE:\n{'-'*40}\n{message[:100]}...\n{'-'*40}")
    
    # 1. Count Tokens
    count_response = client.models.count_tokens(
        model="gemini-2.5-flash",
        contents=message
    )
    tokens = count_response.total_tokens
    print(f"🪙 Token Count: {tokens}")
    
    # 2. Budget Logic
    if tokens > 150:
        print("⚠️ BLOCKED/TRUNCATED: Message exceeds 150 token budget!")
        print("   Running 'overflow_summarize.v1'...")
        
        prompt = OVERFLOW_SUMMARIZE_PROMPT.format(message=message)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        summary = response.text.strip()
        print(f"✅ COMPRESSED SUMMARY: {summary}")
        return summary
    else:
        print("✅ ACCEPTED: Message is within budget.")
        return message

def main():
    print("==========================================================")
    print(" PART 4: THE BUDGET KEEPER (TOKEN ECONOMICS)              ")
    print("==========================================================\n")
    
    # Message 1: Short / Normal
    msg_short = "SOS: 5 people trapped on a roof in Ja-Ela. Water rising fast. Need boat immediately."
    
    # Message 2: Long Spam / Irrelevant noise padded out
    msg_spam = (
        "Hello to whoever is reading this. I hope you are having a blessed day. "
        "I am writing this because I saw on the news that there is a lot of rain "
        "happening right now in the Western Province. My sister called me from Australia "
        "and she was very worried about us. I told her we are fine. The weather here in "
        "Colombo is okay, just a bit cloudy. Also, please share this forward to 10 people "
        "so that everyone stays safe. God bless Sri Lanka. Oh, by the way, I think I saw "
        "a fallen tree near the Jawatte road which might slow down traffic. Anyway, stay safe "
        "everyone. Please reply if you get this. " * 3  # Repeat to ensure > 150 tokens
    )
    
    process_message(msg_short)
    process_message(msg_spam)

if __name__ == "__main__":
    main()
