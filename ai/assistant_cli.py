"""
PAYMENTIQ Grounded Analytics Terminal Interface ("Ask PAYMENTIQ")
Interactive command-line tool allowing stakeholders to ask natural-language business questions.
"""
import sys
import argparse
from ai.nl_engine import assistant_engine

def run_cli():
    parser = argparse.ArgumentParser(description="Ask PAYMENTIQ Grounded Analytics Console")
    parser.add_argument("question", nargs="*", help="Natural-language business question")
    args = parser.parse_args()

    if args.question:
        user_query = " ".join(args.question)
        res = assistant_engine.ask(user_query)
        print("\n" + "="*70)
        print(f"QUESTION: {res['question']}")
        print(f"INTENT:   {res['intent']}")
        print("="*70)
        print(f"\nANSWER:\n{res['answer']}\n")
        print("="*70)
        print("VERIFIED UNDERLYING SQL QUERY:")
        print(res['source_query'])
        print("="*70 + "\n")
    else:
        print("\n======================================================================")
        print(" Welcome to PAYMENTIQ Grounded Analytics Console ('Ask PAYMENTIQ')")
        print(" Type a business question below, or 'exit' / 'quit' to exit.")
        print("======================================================================\n")

        sample_questions = [
            "What is our overall authorization rate and total GTV?",
            "Which payment method has the highest authorization rate?",
            "How much revenue are we losing to payment declines?",
            "Which merchants have the highest addressable leakage?",
            "What are our customer segments and how much do Champions spend?",
            "What is our average support ticket resolution time?"
        ]
        print("Sample Questions to Try:")
        for i, q in enumerate(sample_questions, 1):
            print(f"  {i}. {q}")
        print("\n" + "-"*70)

        while True:
            try:
                user_input = input("\nAsk PAYMENTIQ > ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("Exiting PAYMENTIQ Console. Goodbye!")
                    break

                res = assistant_engine.ask(user_input)
                print("\n" + "="*70)
                print(f"INTENT: {res['intent']}")
                print("="*70)
                print(f"\n{res['answer']}\n")
                print("="*70)
                print("SOURCE SQL:")
                print(res['source_query'])
                print("="*70)

            except (KeyboardInterrupt, EOFError):
                print("\nSession ended.")
                break

if __name__ == "__main__":
    run_cli()
