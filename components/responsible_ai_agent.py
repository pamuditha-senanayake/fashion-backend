# backend/components/responsible_ai_agent.py
import pandas as pd
import asyncio
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class ResponsibleAIAgent:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    async def _call_detail_agent(self, df: pd.DataFrame) -> str:
        """
        Summarize raw trend records into detailed audit points.
        """
        records = df[['trend_name', 'predicted_trend_score', 'forecasted_trend_score', 'trendDirection']].to_dict(orient='records')
        prompt = (
            "You are a Responsible AI Auditor. Analyze the following fashion trend data and "
            "identify potential issues regarding fairness, bias, transparency, explainability, "
            "forecast reliability, or data quality. Output as concise bullet points separated by semicolons.\n\n"
            f"Trend Data:\n{records}\n\n"
            "Output points separated by semicolons."
        )

        resp = await self.client.chat.completions.acreate(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400
        )

        return resp.choices[0].message.content.strip()

    async def _call_summary_agent(self, detail_points: str) -> str:
        """
        Condense detailed points into exactly 10 audit points max.
        """
        prompt = (
            "You are a Responsible AI Auditor. Summarize the following audit points into "
            "a concise report containing exactly 10 distinct points, semicolon-separated:\n\n"
            f"{detail_points}"
        )

        resp = await self.client.chat.completions.acreate(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )

        return resp.choices[0].message.content.strip()

    async def audit_trends(self, df_final: pd.DataFrame) -> pd.DataFrame:
        # Step 1: Detail Agent
        try:
            detail_points = await self._call_detail_agent(df_final)
        except Exception:
            detail_points = "AI failed to generate detailed audit points."

        # Step 2: Summary Agent
        try:
            summary_points = await self._call_summary_agent(detail_points)
        except Exception:
            summary_points = "AI failed to generate summarized audit points."

        # Return a single-row DataFrame for frontend
        df_audit = pd.DataFrame([{
            "trend_name": "All Trends",
            "ai_audit_notes": summary_points
        }])

        return df_audit
