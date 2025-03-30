from ..functions.embedding import generate_embedding
from ..functions.iris import fetch_notes
from ..functions.llm import answer_query
from ..utils.similarity import cosine_similarity
import logging
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*NumPy: _ARRAY_API not found.*")

logger = logging.getLogger("clinical_assistant.search")


def hybrid_search(query, notes, k=3, vector_weight=0.7):
    """Perform hybrid search combining vector similarity and keyword matching"""
    try:
        # Get query embedding
        query_embedding = generate_embedding(query)

        # Vector similarity component
        vector_scores = [
            {
                "patient_id": n.get("patient_id", "unknown"),
                "note_id": n["note_id"],
                "text": n["text"],
                "score": cosine_similarity(query_embedding, n["embedding"])
            }
            for n in notes
        ]

        # Keyword matching component
        query_terms = set(query.lower().split())
        keyword_scores = []

        for n in notes:
            text = n["text"].lower()
            # Calculate how many query terms appear in the text
            matches = sum(1 for term in query_terms if term in text)
            score = matches / len(query_terms) if query_terms else 0

            keyword_scores.append({
                "patient_id": n.get("patient_id", "unknown"),
                "note_id": n["note_id"],
                "text": n["text"],
                "score": score
            })

        # Combine scores
        combined_scores = []
        for i in range(len(notes)):
            combined_score = (
                    vector_weight * vector_scores[i]["score"] +
                    (1 - vector_weight) * keyword_scores[i]["score"]
            )

            combined_scores.append({
                "patient_id": notes[i].get("patient_id", "unknown"),
                "note_id": notes[i]["note_id"],
                "text": notes[i]["text"],
                "score": combined_score
            })

        # Sort and return top-k
        top_results = sorted(combined_scores, key=lambda x: x["score"], reverse=True)[:k]
        logger.info(f"Hybrid search returned {len(top_results)} results")
        return top_results

    except Exception as e:
        logger.error(f"Error in hybrid search: {str(e)}")
        return []


def rag_pipeline(query, k=3):
    """Complete RAG pipeline for clinical queries"""
    logger.info(f"Processing query: '{query}'")

    # 1. Retrieve notes from database
    notes = fetch_notes()

    # 2. Perform hybrid search for relevant context
    top_notes = hybrid_search(query, notes, k=k)

    # 3. Generate answer with context
    answer = answer_query(query, top_notes)

    return answer, top_notes