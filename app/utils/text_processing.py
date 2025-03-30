import re


def clean_llm_response(response):
    """
    Clean up LLM response text with filtering for system messages,
    tags, and other unwanted content
    """
    # First, remove all tagged sections
    response = re.sub(r'<[^>]+>.*?</[^>]+>', '', response, flags=re.DOTALL)

    # Remove any remaining tags
    response = re.sub(r'<[^>]+>', '', response)

    # Remove code block indicators
    response = re.sub(r'```[^`]*```', '', response)
    response = re.sub(r'```.*$', '', response, flags=re.DOTALL)

    # Remove any text that looks like raw patient data
    response = re.sub(r'Patient \d+ has (the following|undergone).+?(:|\n)', '', response)
    response = re.sub(r'- [^\n]+\n', '', response)

    # Remove meta-phrases about answering
    response = re.sub(r'Please note that.*?question', '', response, flags=re.DOTALL | re.IGNORECASE)
    response = re.sub(r'Let me know if this meets.*', '', response, flags=re.DOTALL | re.IGNORECASE)
    response = re.sub(r'The answer should be.*', '', response, flags=re.DOTALL | re.IGNORECASE)
    response = re.sub(r'I should.*', '', response, flags=re.DOTALL | re.IGNORECASE)

    # Remove self-reflective statements
    response = re.sub(r'Based on the information provided.*?,', '', response)
    response = re.sub(r'According to the patient data.*?,', '', response)

    # Remove other standard artifacts
    response = re.sub(r'Best regards,.*', '', response, flags=re.DOTALL)
    response = re.sub(r'Sincerely,.*', '', response, flags=re.DOTALL)
    response = re.sub(r'Thanks,.*', '', response, flags=re.DOTALL)

    # Remove any disclaimer-like statements
    response = re.sub(r'Note:.*', '', response)
    response = re.sub(r'Disclaimer:.*', '', response)

    # Split into sentences and remove duplicates
    sentences = [s.strip() for s in re.split(r'[.!?]', response) if s.strip()]
    unique_sentences = []
    for sentence in sentences:
        if sentence and sentence not in unique_sentences and len(sentence) > 5:
            unique_sentences.append(sentence)

    # Clean up and rejoin
    clean_response = '. '.join(unique_sentences)
    if clean_response and not clean_response.endswith('.'):
        clean_response += '.'

    # Final cleanup of any remaining weird artifacts
    clean_response = re.sub(r'\s{2,}', ' ', clean_response)

    # Handle empty responses
    if not clean_response or clean_response.isspace():
        return "I couldn't generate a clear answer. Please try rephrasing your question."

    return clean_response