from huggingface_hub import InferenceClient
import logging
from functools import lru_cache
from ..config.config import load_config
from ..utils.text_processing import clean_llm_response

logger = logging.getLogger("clinical_assistant.llm")
config = load_config()


@lru_cache(maxsize=1)
def get_hf_client():
    """Get and cache Hugging Face client"""
    logger.info("Initializing Hugging Face client")
    return InferenceClient(token=config["llm"]["api_key"])


def generate_text(prompt, model=None, max_length=None, temperature=None, top_p=None):
    """Generate text using Hugging Face API"""
    model = model or config["llm"]["model"]
    max_length = max_length or config["llm"]["max_length"]
    temperature = temperature or config["llm"]["temperature"]
    top_p = top_p or config["llm"]["top_p"]

    try:
        client = get_hf_client()
        logger.info(f"Generating text with model: {model}")

        response = client.text_generation(
            prompt,
            model=model,
            max_new_tokens=max_length,
            temperature=temperature,
            top_p=top_p
        )

        return response
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        return f"Error generating response: {str(e)}"


def answer_query(query, context_notes, include_sources=True):
    """Generate answer to a query using LLM with improved prompt"""
    try:
        # Format context with patient IDs
        context_items = []
        for i, n in enumerate(context_notes):
            patient_id = n.get("patient_id", "Unknown")
            context_items.append(f"[Patient {patient_id}]\n{n['text']}")

        context = "\n\n".join(context_items)

        # Create prompt with stronger formatting instructions
        prompt = f"""
You are a clinical assistant AI helping healthcare professionals.
TASK: Answer the following question using ONLY the patient data provided below.

FORMAT REQUIREMENTS:
- Provide ONLY the answer with absolutely no postamble, or meta-commentary
- Do not repeat the question
- Do not include phrases like "Based on the information provided" or "According to the data"
- Keep your answer to 1-2 sentences maximum
- Do not include any disclaimers, notes, or caveats
- Do not mention the PATIENT DATA section itself

PATIENT DATA:
{context}

QUESTION: {query}

DIRECT ANSWER:
"""

        # Generate and clean response
        response = generate_text(prompt)
        clean_response = clean_llm_response(response)

        # Add sources if requested
        if include_sources:
            sources = [f"Patient {n.get('patient_id', 'Unknown')}" for n in context_notes]
            source_text = f"\n\nSources: {', '.join(sources)}"
            return clean_response + source_text

        return clean_response

    except Exception as e:
        logger.error(f"Error answering query: {str(e)}")
        return "I encountered an error while generating a response. Please try again."