from app6.intent.intent_classifier import IntentClassifier


def main():

    classifier = IntentClassifier()

    while True:

        query = input("\nEnter Query (exit/quit/q to quit): ").strip()

        if query.lower() in ["exit", "quit", "q"]:

            print("\nExiting...")

            break

        try:

            result = classifier.classify(query)

            print("\nIntent Classification Result")
            print("-" * 40)

            print(f"Intent      : {result.intent}")
            print(f"Confidence  : {result.confidence}")
            print(f"Reason      : {result.reason}")

        except Exception as e:

            print(f"\nError : {e}")


if __name__ == "__main__":
    main()
