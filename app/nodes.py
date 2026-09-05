from app.state import State
from app.llm import create_llm
from app.schemas import PlannerDecision
from app.state import State
from app.tools.financial_metrics import get_financial_metrics

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

def financial_data_node(state: State):
    print("[financial_data_node started]")

    ticker = state["ticker"]

    financial_data = get_financial_metrics(
        ticker=ticker
    )

    return {
        "financial_data": financial_data
    }

def news_node(state: State):
    print("[news_node started]")

    ticker = state["ticker"]

    news = [
        {
            "title": f"Example recent news article for {ticker}",
            "source": "Example News",
        }
    ]

    return {
        "news": news
    }

def transcript_node(state: State):
    print("[transcript_node started]")

    ticker = state["ticker"]

    transcript = (
        f"Example earnings call transcript for {ticker}. "
        "Management expressed optimism about the next quarter."
    )

    return {
        "transcript": transcript
    }

def sec_filing_node(state: State):
    print("[sec_filing_node started]")

    ticker = state["ticker"]

    sec_filing = (
        f"Example SEC filing for {ticker}. "
        "The company highlighted several operational and financial risks."
    )

    return {
        "sec_filing": sec_filing
    }


def retrieval_complete_node(state: State):
    print("[retrieval_complete_node started]")

    return {}


def financial_analyst_node(state: State):
    print("[financial_analyst_node started]")

    financial_data = state.get("financial_data")

    if financial_data is None:
        return {
            "financial_analysis": (
                "Financial analysis was skipped because "
                "financial metrics were not requested."
            )
        }

    ticker = financial_data["ticker"]

    latest_revenue = financial_data.get(
        "latest_quarter_revenue"
    )

    actual_eps = financial_data.get(
        "latest_reported_eps"
    )

    estimated_eps = financial_data.get(
        "latest_eps_estimate"
    )

    surprise_percent = financial_data.get(
        "latest_eps_surprise_percent"
    )

    analysis_parts = [
        f"Financial metrics were retrieved for {ticker}."
    ]

    if latest_revenue is not None:
        analysis_parts.append(
            f"Latest quarterly revenue: {latest_revenue:,.0f}."
        )

    if actual_eps is not None:
        analysis_parts.append(
            f"Latest reported EPS: {actual_eps:.2f}."
        )

    if estimated_eps is not None:
        analysis_parts.append(
            f"Consensus EPS estimate: {estimated_eps:.2f}."
        )

    if surprise_percent is not None:
        analysis_parts.append(
            f"EPS surprise: {surprise_percent:.2f}%."
        )

    return {
        "financial_analysis": " ".join(
            analysis_parts
        )
    }
def risk_assessment_node(state: State):
    print("[risk_assessment_node started]")

    financial_data = state.get("financial_data")
    sec_filing = state.get("sec_filing")

    if financial_data is None and sec_filing is None:
        return {
            "risk_analysis": (
                "Risk analysis was skipped because "
                "risk-related data was not requested."
            )
        }

    risk_parts = []

    if financial_data is not None:
        debt_to_ebitda = financial_data.get(
            "debt_to_ebitda"
        )

        if debt_to_ebitda is not None:
            risk_parts.append(
                f"Debt-to-EBITDA is "
                f"{debt_to_ebitda:.2f}."
            )

    if sec_filing is not None:
        risk_parts.append(
            f"SEC filing data: {sec_filing}"
        )

    if not risk_parts:
        risk_parts.append(
            "No usable risk metrics were available."
        )

    return {
        "risk_analysis": " ".join(risk_parts)
    }

def report_generator_node(state: State):
    print("[report_generator_node executed]")

    report = f"""
    # Finance Bot Report

    ## Company

    {state["ticker"]}

    ## Financial Analysis

    {state["financial_analysis"]}

    ## Risk Analysis

    {state["risk_analysis"]}
    """

    return {"final_report": report}