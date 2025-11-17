def compute_final_score(face_metrics, voice_metrics, nlp_metrics):
    """
    Weighted scoring:
      - eye contact / attention 20%
      - voice confidence 25%
      - hesitation 15%
      - answer quality 40%
    face_metrics example fields: eye_contact_percent
    voice_metrics example fields: avg_energy, hesitation_count
    nlp_metrics: final_quality_score (0-100)
    """
    eye = face_metrics.get("eye_contact_percent", 0)
    # map energy to confidence (normalize roughly)
    energy = voice_metrics.get("avg_energy", 0)
    # simple normalization
    voice_confidence = min(100, max(20, int(energy * 1000)))  # placeholder mapping
    hesitation = voice_metrics.get("hesitation_count", 0)
    hesitation_score = max(0, 100 - hesitation * 10)  # each long silence reduces score

    answer_quality = nlp_metrics.get("final_quality_score", 50)

    score = (
        0.20 * eye +
        0.25 * voice_confidence +
        0.15 * hesitation_score +
        0.40 * answer_quality
    )
    return round(score, 2)
