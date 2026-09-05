from app.state import State
from app.llm import create_llm
from app.schemas import PlannerDecision
from app.state import State

llm = create_llm()
planner_llm = llm.with_structured_output(
    PlannerDecision,
    method="json_schema",
)

PLANNER_SYSTEM_PROMPT = """
You are the planning component of Finance Bot, a financial research and risk analysis agent.

Your job is to analyze the user's request and decide which data sources are required.

Follow these rules:

1. Identify the company's stock ticker symbol.

2. Set needs_financials to true when the user asks about:
   - revenue
   - earnings
   - EPS
   - valuation
   - P/E ratio
   - debt
   - financial performance
   - earnings results

3. Set needs_news to true when the user asks about:
   - recent price movements
   - sudden stock drops or increases
   - recent company developments
   - analyst upgrades or downgrades
   - regulatory news
   - breaking news

4. Set needs_transcript to true when the user asks about:
   - management commentary
   - guidance
   - earnings calls
   - future expectations
   - analyst questions and management answers

5. Set needs_sec_filing to true when the user asks about:
   - company risks
   - legal proceedings
   - debt disclosures
   - risk factors
   - official regulatory filings
   - 10-Q or 10-K reports

Multiple data sources may be required for a single request.

Select only the data sources that are necessary.

Do not answer the user's financial question.
Only produce the planning decision.
"""

def planner_node(state: State):
    print("\n[planner_node started]")

    user_query = state["user_query"]

    result = planner_llm.invoke(
        [
            (
                "system",
                PLANNER_SYSTEM_PROMPT,
            ),
            (
                "human",
                user_query,
            ),
        ]
    )

    plan = []

    if result.needs_financials:
        plan.append("financial_metrics")

    if result.needs_news:
        plan.append("company_news")

    if result.needs_transcript:
        plan.append("earnings_transcript")

    if result.needs_sec_filing:
        plan.append("sec_filing")

    ticker = result.ticker.strip().upper()

    print("Ticker:", ticker)
    print("Plan:", plan)
    print("Summary:", result.plan_summary)

    return {
        "ticker": ticker,
        "plan": plan,
        "needs_financials": result.needs_financials,
        "needs_news": result.needs_news,
        "needs_transcript": result.needs_transcript,
        "needs_sec_filing": result.needs_sec_filing,
        "planner_summary": result.plan_summary,
    }

def data_retrieval_node(state: State):
    print("[data_retrieval_node executed]")

    ticker = state["ticker"]

    fake_financial_data = {
        "ticker": ticker,
        "revenue": 100_000_000,
        "eps": 2.15,
        "pe_ratio": 24.3,
        "debt_to_ebitda": 1.8,
    }

    return {
        "financial_data": fake_financial_data,
        "news": [
            {
                "title": f"Sample news for {ticker}"
            }
        ],
        "transcript": "Management stated they are optimistic about the next quarter.",
        "sec_filing": "The company highlighted certain operational risks.",
    }


def financial_analyst_node(state: State):
    print("[financial_analyst_node executed]")

    financial_data = state["financial_data"]

    analysis = (
        f"EPS for {financial_data['ticker']} "
        f"was reported as {financial_data['eps']}."
    )

    return {
        "financial_analysis": analysis
    }


def risk_assessment_node(state: State):
    print("[risk_assessment_node executed]")

    debt_to_ebitda = state["financial_data"]["debt_to_ebitda"]

    risk_analysis = (
        f"Debt-to-EBITDA ratio is {debt_to_ebitda}. "
        "Generated sample risk analysis for now."
    )

    return {
        "risk_analysis": risk_analysis
    }


def report_generator_node(state: State):
    print("[report_generator_node executed]")

    report = f"""
# FinSight Report

## Company

{state["ticker"]}

## Financial Analysis

{state["financial_analysis"]}

## Risk Analysis

{state["risk_analysis"]}
"""

    return {
        "final_report": report
    }