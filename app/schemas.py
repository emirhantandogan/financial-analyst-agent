from pydantic import BaseModel, Field


class PlannerDecision(BaseModel):
    ticker: str = Field(
        description="The stock ticker symbol of the company, for example AAPL, TSLA, or NVDA."
    )

    needs_financials: bool = Field(
        description="Whether financial metrics such as revenue, EPS, valuation, or debt are required."
    )

    needs_news: bool = Field(
        description="Whether recent company news, analyst actions, or market developments are required."
    )

    needs_transcript: bool = Field(
        description="Whether earnings call transcripts or management commentary are required."
    )

    needs_sec_filing: bool = Field(
        description="Whether SEC filings such as 10-Q or 10-K reports are required."
    )

    plan_summary: str = Field(
        description="A short explanation of why the selected data sources are required."
    )