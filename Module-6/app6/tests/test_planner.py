from app6.planners.planner import Planner


def main():

    planner = Planner()

    while True:

        query = input("\nEnter Query (exit/quit/q): ").strip()

        if query.lower() in {
            "exit",
            "quit",
            "q",
        }:

            print("\nExiting...")
            break

        if not query:

            print("\nPlease enter a valid query.")

            continue

        intent = input("Enter Intent: ").strip()

        if not intent:

            print("\nIntent cannot be empty.")

            continue

        state = {
            "query": query,
            "intent": intent,
        }

        try:

            result = planner.create_plan(state)

            print("\n")
            print("=" * 80)
            print("PLANNER RESULT")
            print("=" * 80)

            print(f"\nQuery : {query}")

            print(f"Intent : {intent}")

            print("\nPlan:")

            for index, step in enumerate(
                result["plan"],
                start=1,
            ):

                print(f"{index}. {step}")

            print(f"\nReason: " f"{result['plan_reason']}")

            print("=" * 80)

        except Exception as e:

            print(f"\nPlanning failed: {e}")


if __name__ == "__main__":
    main()
