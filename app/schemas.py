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

class FinancialAnalysisResult(BaseModel):
    summary: str = Field(
        description="A concise overall financial interpretation of the available evidence."
    )

    key_findings: list[str] = Field(
        description="The most important findings supported by the provided financial data and news."
    )

    market_reaction_explanation: str = Field(
        description="The most likely explanation for the market reaction based only on the provided evidence."
    )

    confirmed_facts: list[str] = Field(
        description="Facts that are directly supported by the provided data or article content."
    )

    inferences: list[str] = Field(
        description="Reasonable interpretations that are not directly confirmed facts."
    )