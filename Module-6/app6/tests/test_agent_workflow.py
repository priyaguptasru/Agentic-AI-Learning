from app6.workflows.agent_workflow import (
    AgentWorkflow,
)


def main():

    workflow = AgentWorkflow()

    while True:

        query = input("\nEnter Query " "(exit/quit/q): ").strip()

        if query.lower() in [
            "exit",
            "quit",
            "q",
        ]:

            print("\nExiting...")

            break

        if not query:

            print("\nPlease enter a valid query.")

            continue

        try:

            response = workflow.run(query)

            print("\n")
            print("=" * 80)
            print("FINAL RESULT")
            print("=" * 80)

            print(f"\nQuery   : " f"{response.get('query')}")

            print(f"Intent  : " f"{response.get('intent')}")

            print(f"Plan    : " f"{response.get('plan')}")

            print("\nSteps Executed:")

            for step in response.get(
                "steps_executed",
                [],
            ):

                print(f"  ✓ {step}")

            print("\nAnswer:")

            print(
                response.get(
                    "answer",
                    "No answer generated.",
                )
            )

            print("=" * 80)

        except Exception as e:

            print(f"\nError: {e}")


if __name__ == "__main__":

    main()
