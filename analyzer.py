"""
AI Analyzer (Ye hai asli "Agent" wala kaam)
--------------------------------------------
Cleaned data ka statistical summary banata hai, phir usko Claude API
ko bhejta hai taaki:
  1. Human-readable insights nikaal sake
  2. Trends/anomalies point out kar sake
  3. Business-relevant recommendations de sake

IMPORTANT: Isko chalane ke liye environment variable set karo:
  export ANTHROPIC_API_KEY="your-key-here"

API key yahan (https://console.anthropic.com) se milegi.
"""

import os
import json
import pandas as pd


def _build_data_summary(df: pd.DataFrame) -> str:
    """DataFrame ka compact summary banata hai - poora raw data AI ko nahi bhejte,
    sirf stats bhejte hain (fast + cheap + privacy-friendly)."""

    summary_parts = []
    summary_parts.append(f"Total rows: {len(df)}, Total columns: {len(df.columns)}")
    summary_parts.append(f"Columns: {list(df.columns)}")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        summary_parts.append("\nNumeric column statistics:")
        summary_parts.append(df[numeric_cols].describe().to_string())

    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    for col in categorical_cols[:5]:  # zyada columns bhejne se bachna hai
        top_values = df[col].value_counts().head(5).to_dict()
        summary_parts.append(f"\nTop values in '{col}': {top_values}")

    date_cols = df.select_dtypes(include="datetime").columns.tolist()
    if date_cols:
        for col in date_cols:
            summary_parts.append(f"\nDate range in '{col}': {df[col].min()} to {df[col].max()}")

    return "\n".join(summary_parts)


def generate_insights(df: pd.DataFrame, ai_config: dict) -> dict:
    """
    Returns dict:
    {
        "summary": "...",
        "insights": ["...", "...", ...],
        "recommendations": ["...", "...", ...]
    }
    """

    if not ai_config.get("enabled", True):
        return {"summary": "AI analysis disabled in config.", "insights": [], "recommendations": []}

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[AI Analyzer] WARNING: ANTHROPIC_API_KEY nahi mili. "
              "Fallback basic statistical summary use ho raha hai.")
        return _fallback_summary(df)

    try:
        import anthropic
    except ImportError:
        print("[AI Analyzer] 'anthropic' package installed nahi hai. Run: pip install anthropic")
        return _fallback_summary(df)

    data_summary = _build_data_summary(df)
    domain_hint = ai_config.get("domain_hint", "general business data")
    max_insights = ai_config.get("max_insights", 6)
    model = ai_config.get("model", "claude-sonnet-4-6")

    prompt = f"""Tum ek business data analyst AI agent ho. Neeche di gayi dataset summary ({domain_hint}) ko dekho:

{data_summary}

Mujhe STRICT JSON format mein jawab do (koi extra text nahi, sirf JSON):
{{
  "summary": "2-3 line overall summary",
  "insights": ["insight 1", "insight 2", ... up to {max_insights} insights],
  "recommendations": ["recommendation 1", "recommendation 2", ...]
}}

Insights specific, numbers-based aur actionable hone chahiye. Generic baatein mat likho."""

    client = anthropic.Anthropic(api_key=api_key)
    print(f"[AI Analyzer] Calling Claude ({model}) for insights...")

    response = client.messages.create(
        model=model,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        print("[AI Analyzer] JSON parse fail hua, raw text return kar rahe hain.")
        result = {"summary": raw_text, "insights": [], "recommendations": []}

    return result


def _fallback_summary(df: pd.DataFrame) -> dict:
    """Agar API key na ho to bhi basic (non-AI) insights de dete hain,
    taaki pipeline pura chal sake."""

    insights = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    for col in numeric_cols[:4]:
        insights.append(
            f"'{col}' ka average = {df[col].mean():.2f}, max = {df[col].max():.2f}, min = {df[col].min():.2f}"
        )

    return {
        "summary": f"Dataset mein {len(df)} rows aur {len(df.columns)} columns hain. "
                   f"(Ye basic statistical summary hai - AI insights ke liye ANTHROPIC_API_KEY set karo)",
        "insights": insights,
        "recommendations": ["Deeper insights ke liye ANTHROPIC_API_KEY environment variable set karein."],
    }
