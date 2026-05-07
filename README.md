# 🌊 Operation Ditwah: AI-Driven Disaster Relief Triage

Operation Ditwah is a comprehensive **Prompt Engineering** framework designed for mission-critical disaster relief operations in Sri Lanka. It demonstrates how to leverage Large Language Models (LLMs) like Gemini to automate crisis triage, ensure logical reasoning in high-stakes environments, and manage operational costs through structured data and token economics.

![Disaster Relief AI Dashboard](file:///C:/Users/Taruni/.gemini/antigravity/brain/9e1ac2bf-7208-4291-a5dd-c5684f2fa29a/disaster_relief_ai_dashboard_1778134270180.png)

## 🚀 Project Overview

During a disaster, information is chaotic, unstructured, and overwhelming. This project implements a multi-stage AI pipeline to transform raw SOS messages and news feeds into actionable, structured logistics data.

### Key Technical Pillars:
1.  **Few-Shot Classification**: Using 8-example prompts to extract District, Intent, and Priority with high precision.
2.  **LLM Stability Control**: A deep dive into the impact of `temperature` on triage reliability (Safety vs. Chaos drift).
3.  **Advanced Reasoning (CoT & ToT)**: Implementing *Chain-of-Thought* for transparent scoring and *Tree-of-Thoughts* for optimal rescue routing.
4.  **Token Economics**: Real-time token counting and aggressive summarization to maintain budget constraints during high-volume crises.
5.  **Structured JSON Pipelines**: Using **Pydantic** models to force LLMs into strict JSON schemas for seamless Excel/Database integration.

---

## 🛠️ Tech Stack
- **AI Core**: Google Gemini 2.5 Flash
- **Language**: Python 3.10+
- **Data Handling**: Pandas, Pydantic, Regex
- **API Management**: Google GenAI SDK, Dotenv

---

## 📂 Project Structure

### [Part 1: The Few-Shot Classifier](part1.py)
Automates the classification of 49+ raw emergency messages. Uses structured few-shot prompting to categorize by district and priority, exporting results to a clean Excel report.

### [Part 2: The Stability Experiment](part2.py)
A "Temperature Stress Test" comparing **Safe Mode (0.0)** vs. **Chaos Mode (1.0)**. Demonstrates how hallucinations in high-temperature settings can lead to fatal triage errors.

### [Part 3: The Logistics Commander](part3.py)
Uses **Chain-of-Thought (CoT)** to reason through victim age and urgency, followed by **Tree-of-Thoughts (ToT)** to explore multiple rescue boat routing paths and pick the optimal sequence.

### [Part 4: The Budget Keeper](part4.py)
Implements a "Token Guardrail." Messages exceeding the 150-token budget are automatically intercepted and compressed into one-sentence actionable summaries to save costs.

### [Part 5: News Feed Extraction Pipeline](part5.py)
Converts unstructured news text into validated JSON objects using Pydantic. Generates a automated `flood_report.xlsx` tracking water levels and victim counts across districts.

---

## 📈 Key Insights
- **Temperature Matters**: For triage, `temperature=0.0` is non-negotiable. High temperature leads to "resource hallucination" (inventing helicopters or generators).
- **Reasoning over Results**: Forcing the model to "think step-by-step" (CoT) significantly reduces logical contradictions in priority scoring.
- **Structured Outputs**: Using `response_mime_type="application/json"` with Pydantic schemas is the most reliable way to build production-ready AI pipelines.

---

## 🔧 Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/[your-username]/operation-ditwah.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env`:
   ```bash
   GEMINI_API_KEY=your_api_key_here
   ```
4. Run the parts:
   ```bash
   python part1.py
   ```

---
*Created as a demonstration of Advanced Prompt Engineering for Humanitarian Aid.*

## 🏆 Acknowledgments
Special thanks to **@[Organization Name]** for providing the project scenario and data that made this simulation possible. This project was developed as part of their [Program Name/Challenge Name] to explore the frontiers of AI in disaster management.