from app.state import State


def planner_node(state: State):
    print("\n[planner_node executed]")

    return {
        "plan": [
            "financial_metrics",
            "company_news",
            "earnings_transcript",
            "sec_filing",
        ]
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