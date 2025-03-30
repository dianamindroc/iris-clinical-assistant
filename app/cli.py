from app.functions.search import rag_pipeline
import logging

logger = logging.getLogger("clinical_assistant.cli")


def cli_interface():
    """Command-line interface for the clinical assistant"""
    print("\n=== IRIS Clinical Assistant ===\n")
    print("Type 'exit' to quit\n")

    while True:
        query = input("\nEnter your clinical query: ")

        if query.lower() == 'exit':
            break

        # Process the query
        try:
            answer, top_notes = rag_pipeline(query)

            print("\nTop retrieved notes:")
            for i, n in enumerate(top_notes):
                print(f"{i + 1}. {n['note_id']} (score {n['score']:.3f}) - Patient {n.get('patient_id', 'Unknown')}")

            print("\nGenerated answer:")
            print(answer)
        except Exception as e:
            logger.exception("Error processing query")
            print(f"Error: {str(e)}")
            print("Please try again or type 'exit' to quit.")


if __name__ == "__main__":
    cli_interface()