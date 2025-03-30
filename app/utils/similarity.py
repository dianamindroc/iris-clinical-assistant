def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    # Convert tensor to list if needed
    if hasattr(a, 'tolist'):
        a = a.tolist()
    if hasattr(b, 'tolist'):
        b = b.tolist()

    # Calculate dot product
    dot_product = sum(x * y for x, y in zip(a, b))

    # Calculate magnitudes
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(x * x for x in b) ** 0.5

    # Return cosine similarity
    return dot_product / (mag_a * mag_b) if mag_a * mag_b > 0 else 0