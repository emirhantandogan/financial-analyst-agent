from app.graph import create_graph


def main():
    graph = create_graph()

    query = input("Ask Finance Bot: ").strip()

    result = graph.invoke(
        {
            "user_query": query
        }
    )

    print("\n----------------------")
    print("FINAL REPORT")
    print("----------------------")

    print(result["final_report"])


if __name__ == "__main__":
    main()