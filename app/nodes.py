import json

from app.state import State
from app.llm import create_llm
from app.schemas import PlannerDecision
from app.state import State
from app.tools.company_news import fetch_company_news
from app.tools.financial_metrics import get_financial_metrics
from app.tools.article_content import fetch_article_content
from app.tools.company_news import fetch_company_news
from app.schemas import (
    FinancialAnalysisResult,
    PlannerDecision,
)

MAX_ARTICLES_WITH_FULL_CONTENT = 3

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

FINANCIAL_ANALYST_SYSTEM_PROMPT = """
You are the financial analysis component of FinSight.

Your job is to analyze the evidence collected by the system and explain what it means.

You may receive:
- financial metrics
- analyst consensus estimates
- recent news summaries
- full article content

Follow these rules:

1. Use only the evidence provided in the input.
2. Do not invent financial figures, events, or management statements.
3. Separate confirmed facts from interpretation.
4. If the evidence is insufficient to explain a market movement, say so clearly.
5. When financial results are available, compare actual results with analyst expectations.
6. When news is available, identify the most plausible catalysts supported by the articles.
7. Do not assume that correlation proves causation.
8. Prefer full article content over headlines when they conflict.
9. Treat search-result summaries as weaker evidence than full article content.
10. Keep the analysis concise and decision-oriented.
"""

llm = create_llm()
planner_llm = llm.with_structured_output(
    PlannerDecision,
    method="json_schema",
)

financial_analyst_llm = llm.with_structured_output(
    FinancialAnalysisResult,
    method="json_schema",
)

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

    news = fetch_company_news(
        ticker=ticker,
        hours_back=24,
    )

    enriched_news = []

    for index, article in enumerate(news):
        enriched_article = dict(article)

        if index < MAX_ARTICLES_WITH_FULL_CONTENT:
            url = article.get("url")

            content = fetch_article_content(
                url=url,
            )

            enriched_article["content"] = content

        else:
            enriched_article["content"] = None

        enriched_news.append(
            enriched_article
        )

    full_content_count = sum(
        1
        for article in enriched_news
        if article.get("content")
    )

    print(
        f"Retrieved {len(enriched_news)} news articles."
    )

    print(
        f"Fetched full content for "
        f"{full_content_count} articles."
    )

    return {
        "news": enriched_news
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


def financial_analyst_node(
    state: State,
):
    print("[financial_analyst_node started]")

    financial_data = state.get(
        "financial_data"
    )

    news = state.get(
        "news",
        [],
    )

    if financial_data is None and not news:
        return {
            "financial_analysis": (
                "Financial analysis was skipped because "
                "no relevant financial or news data was available."
            )
        }

    analysis_context = {
        "user_query": state["user_query"],
        "ticker": state["ticker"],
        "financial_data": financial_data,
        "news": _build_news_context(
            news
        ),
    }

    result = financial_analyst_llm.invoke(
        [
            (
                "system",
                FINANCIAL_ANALYST_SYSTEM_PROMPT,
            ),
            (
                "human",
                json.dumps(
                    analysis_context,
                    indent=2,
                    ensure_ascii=False,
                ),
            ),
        ]
    )

    key_findings = "\n".join(
        f"- {finding}"
        for finding in result.key_findings
    )

    confirmed_facts = "\n".join(
        f"- {fact}"
        for fact in result.confirmed_facts
    )

    inferences = "\n".join(
        f"- {inference}"
        for inference in result.inferences
    )

    financial_analysis = f"""
        ### Summary

        {result.summary}

        ### Key Findings

        {key_findings}

        ### Market Reaction

        {result.market_reaction_explanation}

        ### Confirmed Facts

        {confirmed_facts}

        ### Inferences

        {inferences}
        """.strip()

    return {
        "financial_analysis": financial_analysis
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
    print("[report_generator_node started]")

    news = state.get(
        "news",
        [],
    )

    if news:
        news_lines = []

        for article in news:
            title = (
                article.get("title")
                or "Untitled article"
            )

            source = (
                article.get("source")
                or "Unknown source"
            )

            published_at = (
                article.get("published_at")
                or "Unknown publication time"
            )

            url = article.get("url")

            line = (
                f"- **{title}**\n"
                f"  Source: {source}\n"
                f"  Published: {published_at}"
            )

            if url:
                line += f"\n  URL: {url}"

            news_lines.append(line)

        news_section = "\n\n".join(
            news_lines
        )

    else:
        news_section = (
            "No recent news was retrieved."
        )

    financial_analysis = state.get(
        "financial_analysis",
        "Financial analysis was not generated.",
    )

    risk_analysis = state.get(
        "risk_analysis",
        "Risk analysis was not generated.",
    )

    report = f"""
    # FinSight Report

    ## Company

    {state["ticker"]}

    ## Planner Summary

    {state["planner_summary"]}

    ## Retrieved News

    {news_section}

    ## Financial Analysis

    {financial_analysis}

    ## Risk Analysis

    {risk_analysis}
    """

    return {
        "final_report": report
    }


def _build_news_context(
    news: list[dict],
) -> list[dict]:
    news_context = []

    for article in news:
        news_context.append(
            {
                "title": article.get("title"),
                "source": article.get("source"),
                "published_at": article.get(
                    "published_at"
                ),
                "summary": article.get("summary"),
                "content": article.get("content"),
            }
        )

    return news_context