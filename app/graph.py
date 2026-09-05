from langgraph.graph import END, START, StateGraph

from app.nodes import (
    financial_analyst_node,
    financial_data_node,
    news_node,
    planner_node,
    report_generator_node,
    retrieval_complete_node,
    risk_assessment_node,
    sec_filing_node,
    transcript_node,
)
from app.state import State


def create_graph():
    builder = StateGraph(State)

    builder.add_node("planner", planner_node)

    builder.add_node("financial_data", financial_data_node)
    builder.add_node("news", news_node)
    builder.add_node("transcript", transcript_node)
    builder.add_node("sec_filing", sec_filing_node)
    builder.add_node("retrieval_complete", retrieval_complete_node)
    

    builder.add_node("financial_analyst", financial_analyst_node)
    builder.add_node("risk_assessment", risk_assessment_node)
    builder.add_node("report_generator", report_generator_node)

    builder.add_edge(START, "planner")
    builder.add_conditional_edges(
        "planner",
        route_data_sources,
        [
            "financial_data",
            "news",
            "transcript",
            "sec_filing",
            "retrieval_complete",
        ],
    )
    builder.add_edge("financial_data", "retrieval_complete")
    builder.add_edge("news", "retrieval_complete")
    builder.add_edge("transcript", "retrieval_complete")
    builder.add_edge("sec_filing", "retrieval_complete")
    builder.add_edge("retrieval_complete", "financial_analyst")
    builder.add_edge("financial_analyst", "risk_assessment")
    builder.add_edge("risk_assessment", "report_generator")
    builder.add_edge("report_generator", END)

    graph = builder.compile()

    return graph

def route_data_sources(state: State):
    routes = []

    if state["needs_financials"]:
        routes.append("financial_data")

    if state["needs_news"]:
        routes.append("news")

    if state["needs_transcript"]:
        routes.append("transcript")

    if state["needs_sec_filing"]:
        routes.append("sec_filing")

    if not routes:
        return ["retrieval_complete"]

    return routes