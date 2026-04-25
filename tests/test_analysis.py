"""Unit tests for the pure analysis functions in humanizer_mcp.server."""

from humanizer_mcp.server import (
    calculate_burstiness,
    check_contraction_usage,
    check_first_person,
    check_paragraph_uniformity,
    check_rhetorical_questions,
    compute_risk_score,
    count_em_dashes,
    count_words,
    find_ai_phrases,
    find_ai_vocabulary,
    sentence_lengths,
    split_sentences,
)


def test_count_words_basic():
    assert count_words("hello world") == 2
    assert count_words("") == 0
    assert count_words("one two three four") == 4


def test_split_sentences_handles_abbreviations():
    text = "Dr. Smith went to the store. He bought milk."
    sentences = split_sentences(text)
    assert len(sentences) == 2
    assert sentences[0].startswith("Dr. Smith")


def test_split_sentences_on_punctuation():
    text = "First. Second! Third?"
    assert len(split_sentences(text)) == 3


def test_sentence_lengths():
    text = "One two three. Four five."
    assert sentence_lengths(text) == [3, 2]


def test_burstiness_uniform_is_zero():
    # All sentences same length — zero variation
    assert calculate_burstiness([10, 10, 10, 10]) == 0.0


def test_burstiness_varied_is_higher():
    # Mix of very short and very long
    assert calculate_burstiness([2, 20, 3, 18, 5]) > 0.5


def test_burstiness_handles_degenerate_input():
    assert calculate_burstiness([]) == 0.0
    assert calculate_burstiness([5]) == 0.0
    assert calculate_burstiness([0, 0]) == 0.0


def test_find_ai_vocabulary_detects_known_words():
    text = "We will delve into this crucial topic to leverage our findings."
    findings = find_ai_vocabulary(text)
    found_words = {f["word"] for f in findings}
    assert {"delve", "crucial", "leverage"} <= found_words


def test_find_ai_vocabulary_whole_word_only():
    # "Delving" should not match the bare word "delve"
    assert find_ai_vocabulary("Delving into something.") == []


def test_find_ai_phrases_detects_cliches():
    text = "It's important to note that this matters. In conclusion, it helps."
    phrases = {f["phrase"] for f in find_ai_phrases(text)}
    assert "it's important to note" in phrases
    assert "in conclusion" in phrases


def test_count_em_dashes():
    assert count_em_dashes("Hello — world") == 1
    assert count_em_dashes("one — two — three") == 2
    assert count_em_dashes("no dashes here") == 0


def test_check_contraction_usage_contractions_present():
    text = "I don't think it's a problem. We've seen this before."
    result = check_contraction_usage(text)
    assert result["contractions_found"] >= 2
    assert result["assessment"] == "human-like"


def test_check_contraction_usage_too_formal():
    text = (
        "I do not think it is a problem. We have seen this before. It is clear that we are going."
    )
    result = check_contraction_usage(text)
    assert result["assessment"].startswith("AI-like")


def test_check_paragraph_uniformity_uniform():
    # Three paragraphs of identical length
    p = "one two three four five six seven eight nine ten."
    result = check_paragraph_uniformity(f"{p}\n\n{p}\n\n{p}")
    assert result["paragraph_count"] == 3
    assert "uniform" in result["assessment"]


def test_check_paragraph_uniformity_varied():
    text = "short.\n\n" + ("word " * 50).strip() + ".\n\nmedium medium medium."
    result = check_paragraph_uniformity(text)
    assert result["coefficient_of_variation"] > 0.4


def test_check_paragraph_uniformity_insufficient_data():
    result = check_paragraph_uniformity("only one paragraph here.")
    assert result["uniformity"] == "insufficient data"


def test_check_rhetorical_questions():
    text = "What if we tried something new? Here is a statement. Is this right?"
    assert check_rhetorical_questions(text) == 2


def test_check_first_person_present():
    text = "I think we should try this. My guess is it will work for us."
    result = check_first_person(text)
    assert result["total_occurrences"] >= 3
    assert "good" in result["assessment"]


def test_check_first_person_absent():
    text = "The system works. It processes data. Results are produced."
    result = check_first_person(text)
    assert "weak" in result["assessment"]


def test_compute_risk_score_low_for_clean_text():
    analysis = {
        "word_count": 150,
        "ai_vocabulary_count": 0,
        "ai_phrase_count": 0,
        "burstiness": 0.6,
        "contractions": {"assessment": "human-like"},
        "paragraph_uniformity": {"assessment": "good variation"},
        "rhetorical_questions": 2,
        "first_person": {"assessment": "good - human voice present"},
        "em_dash_count": 0,
    }
    result = compute_risk_score(analysis)
    assert result["risk_level"] == "LOW"
    assert result["risk_score"] <= 20


def test_compute_risk_score_high_for_aligned_signals():
    analysis = {
        "word_count": 300,
        "ai_vocabulary_count": 10,
        "ai_phrase_count": 5,
        "burstiness": 0.15,
        "contractions": {"assessment": "AI-like (too formal)"},
        "paragraph_uniformity": {"assessment": "too uniform (AI-like)"},
        "rhetorical_questions": 0,
        "first_person": {"assessment": "weak - add personal perspective"},
        "em_dash_count": 8,
    }
    result = compute_risk_score(analysis)
    assert result["risk_level"] == "HIGH"
    assert result["risk_score"] >= 60
    assert len(result["factors"]) >= 5


def test_compute_risk_score_clamps_to_100():
    analysis = {
        "word_count": 500,
        "ai_vocabulary_count": 50,
        "ai_phrase_count": 20,
        "burstiness": 0.1,
        "contractions": {"assessment": "AI-like (too formal)"},
        "paragraph_uniformity": {"assessment": "too uniform (AI-like)"},
        "rhetorical_questions": 0,
        "first_person": {"assessment": "weak - add personal perspective"},
        "em_dash_count": 15,
    }
    assert compute_risk_score(analysis)["risk_score"] <= 100
