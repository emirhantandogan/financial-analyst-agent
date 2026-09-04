from typing import TypedDict  # Type constructor to define dictionary schemas with specific key-value types


class State(TypedDict, total=False):  # Workflow state schema (total=False: all keys are optional)
    user_query: str  # Raw user prompt or analysis request
    ticker: str  # Stock ticker symbol (e.g., AAPL, NVDA)

    plan: list[str]  # Ordered execution steps for the workflow

    financial_data: dict  # Parsed financial statements, ratios, and numeric metrics
    news: list[dict]  # Scraped market news articles and sentiment metadata
    transcript: str  # Text transcript of earnings conference calls
    sec_filing: str  # Raw or processed regulatory filings (e.g., 10-K, 10-Q)

    financial_analysis: str  # Model-generated assessment of company finances
    risk_analysis: str  # Evaluation of operational, market, and business risks

    final_report: str  # Consolidated final research report ready for delivery