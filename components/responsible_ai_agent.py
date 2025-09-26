import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
import traceback
import asyncio

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ResponsibleAIAgent:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        print("[DEBUG] Initializing OpenAI client...")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        print("[DEBUG] OpenAI client initialized successfully.")

    async def _call_detail_agent(self, df: pd.DataFrame) -> str:
        print("[DEBUG] Preparing detailed audit prompt...")

        # --- Pre-aggregate trends to avoid AI complaints ---
        df_agg = df.groupby('trend_name').agg(
            predicted_trend_score_avg=('predicted_trend_score', 'mean'),
            forecasted_trend_score_avg=('forecasted_trend_score', 'mean'),
            trendDirection=('trendDirection', lambda x: x.mode()[0] if not x.mode().empty else 'stable')
        ).reset_index()

        # Optionally add variance info for AI context
        df_agg['predicted_trend_score_var'] = df.groupby('trend_name')['predicted_trend_score'].transform('var').values
        df_agg['forecasted_trend_score_var'] = df.groupby('trend_name')['forecasted_trend_score'].transform('var').values

        records = df_agg.to_dict(orient='records')
        print(f"[DEBUG] Aggregated records to send to AI: {records}")

        prompt = (
            "You are a Responsible AI Auditor. but you should discuss both 50% pros and 50% cons. Analyze the following aggregated fashion trend data and "
            "identify potential issues regarding fairness, bias, transparency, explainability, "
            "forecast reliability, or data quality. Provide concise bullet points separated by semicolons.\n\n"
            f"Trend Data:\n{records}\n\n"
            "Output points separated by semicolons."
        )

        try:
            print("[DEBUG] Sending request to OpenAI (detail agent)...")
            resp = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400
            )
            print("[DEBUG] Response received from detail agent.")
            content = resp.choices[0].message.content.strip()
            print(f"[DEBUG] Detail agent output: {content}")
            return content
        except Exception:
            print("[ERROR] Failed in _call_detail_agent:")
            traceback.print_exc()
            return "AI failed to generate detailed audit points."

    async def _call_summary_agent(self, detail_text: str) -> str:
        print("[DEBUG] Preparing summary audit prompt...")
        print(f"[DEBUG] Detail text: {detail_text}")

        prompt = (
            "You are a Responsible AI Auditor. Mention specific items for personalization. "
            "Summarize the following audit points into a concise report containing exactly 10 distinct points, semicolon-separated:\n\n"
            f"{detail_text}"
        )

        try:
            print("[DEBUG] Sending request to OpenAI (summary agent)...")
            resp = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            print("[DEBUG] Response received from summary agent.")
            content = resp.choices[0].message.content.strip()
            print(f"[DEBUG] Summary agent output: {content}")
            return content
        except Exception:
            print("[ERROR] Failed in _call_summary_agent:")
            traceback.print_exc()
            return "AI failed to generate summarized audit points."

    async def audit_trends(self, df_final: pd.DataFrame) -> pd.DataFrame:
        print("[DEBUG] Starting audit_trends pipeline...")
        try:
            detail_text = await self._call_detail_agent(df_final)
        except Exception:
            print("[ERROR] Exception in detail agent call")
            traceback.print_exc()
            detail_text = "AI failed to generate detailed audit points."

        try:
            summary_text = await self._call_summary_agent(detail_text)
        except Exception:
            print("[ERROR] Exception in summary agent call")
            traceback.print_exc()
            summary_text = "AI failed to generate summarized audit points."

        print(f"[DEBUG] Final summary_text: {summary_text}")
        return pd.DataFrame([{
            "trend_name": "All Trends",
            "ai_audit_notes": summary_text
        }])
