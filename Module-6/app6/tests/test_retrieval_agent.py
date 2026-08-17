from app6.agents.retrieval_agent import RetrievalAgent


def main():

    agent = RetrievalAgent()

    while True:

        query = input("\nEnter Query (exit/quit/q): ").strip()

        if query.lower() in ["exit", "quit", "q"]:
            print("\nExiting...")
            break

        if not query:
            print("\nPlease enter a valid query.")
            continue

        retrieval_response = agent.execute(
            {
                "query": query,
            }
        )

        chunks = retrieval_response["chunks"]

        context = retrieval_response["context"]

        print("\n")
        print("=" * 80)
        print("RETRIEVAL RESULTS")
        print("=" * 80)

        if not chunks:

            print("No matching results found.")
            continue

        for index, result in enumerate(chunks, start=1):

            print(f"\nResult {index}")

            print(f"Document : {result['document']}")
            print(f"Page     : {result['page']}")
            print(f"Section  : {result['section']}")
            print(f"Score     : {result['score']:.4f}")
            print(f"Source    : {result['source']}")

            print("\nText:\n")

            print(result["text"][:300])

            print("-" * 80)

        print("\n")
        print("=" * 80)
        print("GENERATED CONTEXT")
        print("=" * 80)

        print(context)


if __name__ == "__main__":
    main()
