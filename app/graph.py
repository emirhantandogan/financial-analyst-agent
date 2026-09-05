from langgraph.graph import END, START, StateGraph

from app.nodes import (
    data_retrieval_node,
    financial_analyst_node,
    planner_node,
    report_generator_node,
    risk_assessment_node,
)
from app.state import State


def create_graph():
    builder = StateGraph(State)

    builder.add_node("planner", planner_node)
    builder.add_node("data_retrieval", data_retrieval_node)
    builder.add_node("financial_analyst", financial_analyst_node)
    builder.add_node("risk_assessment", risk_assessment_node)
    builder.add_node("report_generator", report_generator_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "data_retrieval")
    builder.add_edge("data_retrieval", "financial_analyst")
    builder.add_edge("financial_analyst", "risk_assessment")
    builder.add_edge("risk_assessment", "report_generator")
    builder.add_edge("report_generator", END)

    graph = builder.compile()

    return graph