import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt', quiet=True)

def evaluate_answer_quality(transcript_text, expected_keywords=None):
    """
    Simple keyword matching & length-based scoring.
    Replace with transformer-based semantic similarity for stronger checks.
    """
    if expected_keywords is None:
        expected_keywords = []

    tokens = [w.lower() for w in word_tokenize(transcript_text)]
    found = [kw for kw in expected_keywords if kw.lower() in tokens]

    length_score = min(1.0, len(tokens) / 50.0)  # 50 tokens -> full
    keyword_score = len(found) / max(1, len(expected_keywords)) if expected_keywords else 0.5

    return {
        "word_count": len(tokens),
        "found_keywords": found,
        "length_score": length_score,
        "keyword_score": keyword_score,
        "final_quality_score": round((length_score * 0.5 + keyword_score * 0.5) * 100, 1)
    }
