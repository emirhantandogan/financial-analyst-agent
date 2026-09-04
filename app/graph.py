from langgraph.graph import StateGraph, START, END

from app.state import State

from app.nodes import (
    planner_node,
    data_retrieval_node,
    financial_analyst_node,
    risk_assessment_node,
    report_generator_node,
)


def create_graph():
    builder = StateGraph(State)

    # Nodes to the graph with their corresponding functions
    builder.add_node("planner", planner_node)

    builder.add_node(
        "data_retrieval",
        data_retrieval_node
    )

    builder.add_node(
        "financial_analyst",
        financial_analyst_node
    )

    builder.add_node(
        "risk_assessment",
        risk_assessment_node
    )

    builder.add_node(
        "report_generator",
        report_generator_node
    )

    # The order of edges defines the execution flow of the graph
    builder.add_edge(
        START,
        "planner"
    )

    builder.add_edge(
        "planner",
        "data_retrieval"
    )

    builder.add_edge(
        "data_retrieval",
        "financial_analyst"
    )

    builder.add_edge(
        "financial_analyst",
        "risk_assessment"
    )

    builder.add_edge(
        "risk_assessment",
        "report_generator"
    )

    builder.add_edge(
        "report_generator",
        END
    )

    graph = builder.compile()

    return graph