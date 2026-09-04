from app.graph import create_graph


def main():
    graph = create_graph()

    ticker = input("Ticker gir: ").strip().upper()

    query = input(
        "FinSight'a sorun: "
    ).strip()

    result = graph.invoke(
        {
            "ticker": ticker,
            "user_query": query,
        }
    )

    print("\n----------------------")
    print("FINAL REPORT")
    print("----------------------")

    print(result["final_report"])


if __name__ == "__main__":
    main()