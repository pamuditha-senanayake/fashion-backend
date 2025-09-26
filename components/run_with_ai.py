# new file: backend/components/run_with_ai.py
from orchestrator import FashionTrendOrchestrator
from responsible_ai_agent import ResponsibleAIAgent
import asyncio

async def main():
    orchestrator = FashionTrendOrchestrator(GEMINI_API_KEY)
    df_final, df_overall = await orchestrator.run_pipeline(limit=50)

    ai_auditor = ResponsibleAIAgent()
    df_final = ai_auditor.audit_trends(df_final)

    print(df_final[['trend_name', 'predicted_trend_score', 'ai_audit_notes', 'ai_audit_summary']])

asyncio.run(main())
