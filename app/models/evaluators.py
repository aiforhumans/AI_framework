"""Built-in evaluators for measuring model/agent performance."""

import re
from typing import Dict, Any, List
from collections import Counter


def tokenize(text: str) -> List[str]:
    """Simple whitespace + punctuation tokenizer."""
    return re.findall(r'\b\w+\b', text.lower())


def f1_score(response: str, ground_truth: str, **kwargs) -> Dict[str, Any]:
    """
    F1 Score: Harmonic mean of precision and recall in token overlaps.
    """
    response_tokens = set(tokenize(response))
    truth_tokens = set(tokenize(ground_truth))

    if not response_tokens or not truth_tokens:
        return {"score": 0.0, "reason": "Empty response or ground truth"}

    common = response_tokens & truth_tokens
    precision = len(common) / len(response_tokens) if response_tokens else 0
    recall = len(common) / len(truth_tokens) if truth_tokens else 0

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    return {
        "score": round(f1, 4),
        "reason": f"Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}"
    }


def bleu_score(response: str, ground_truth: str, n: int = 4, **kwargs) -> Dict[str, Any]:
    """
    BLEU Score: Bilingual Evaluation Understudy for n-gram overlap.
    Simplified implementation without brevity penalty.
    """
    response_tokens = tokenize(response)
    truth_tokens = tokenize(ground_truth)

    if not response_tokens or not truth_tokens:
        return {"score": 0.0, "reason": "Empty response or ground truth"}

    def ngrams(tokens: List[str], n: int) -> List[tuple]:
        return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

    scores = []
    for i in range(1, min(n + 1, len(response_tokens) + 1)):
        resp_ngrams = Counter(ngrams(response_tokens, i))
        truth_ngrams = Counter(ngrams(truth_tokens, i))

        overlap = sum((resp_ngrams & truth_ngrams).values())
        total = sum(resp_ngrams.values())

        if total > 0:
            scores.append(overlap / total)
        else:
            scores.append(0.0)

    if not scores:
        return {"score": 0.0, "reason": "Could not compute n-gram overlap"}

    # Geometric mean of n-gram precisions
    from functools import reduce
    import math
    product = reduce(lambda x, y: x * y, scores, 1.0)
    bleu = math.pow(product, 1.0 / len(scores)) if product > 0 else 0.0

    return {
        "score": round(bleu, 4),
        "reason": f"BLEU-{n} score based on n-gram overlap"
    }


def similarity_score(response: str, ground_truth: str, **kwargs) -> Dict[str, Any]:
    """
    Simple word-level Jaccard similarity.
    """
    response_tokens = set(tokenize(response))
    truth_tokens = set(tokenize(ground_truth))

    if not response_tokens and not truth_tokens:
        return {"score": 1.0, "reason": "Both empty"}

    if not response_tokens or not truth_tokens:
        return {"score": 0.0, "reason": "One side is empty"}

    intersection = len(response_tokens & truth_tokens)
    union = len(response_tokens | truth_tokens)

    sim = intersection / union if union > 0 else 0.0

    return {
        "score": round(sim, 4),
        "reason": f"Jaccard similarity: {intersection}/{union} tokens"
    }


def exact_match(response: str, ground_truth: str, **kwargs) -> Dict[str, Any]:
    """
    Exact match: 1.0 if response equals ground truth (case-insensitive), else 0.0.
    """
    match = response.strip().lower() == ground_truth.strip().lower()
    return {
        "score": 1.0 if match else 0.0,
        "reason": "Exact match" if match else "No exact match"
    }


def contains_match(response: str, ground_truth: str, **kwargs) -> Dict[str, Any]:
    """
    Contains match: 1.0 if ground truth is contained in response.
    """
    match = ground_truth.strip().lower() in response.strip().lower()
    return {
        "score": 1.0 if match else 0.0,
        "reason": "Ground truth found in response" if match else "Ground truth not found"
    }


def length_ratio(response: str, ground_truth: str, **kwargs) -> Dict[str, Any]:
    """
    Length ratio: Ratio of response length to ground truth length.
    Score is 1.0 when lengths are equal, decreases as they diverge.
    """
    resp_len = len(response)
    truth_len = len(ground_truth)

    if truth_len == 0:
        return {"score": 0.0 if resp_len > 0 else 1.0, "reason": "Ground truth is empty"}

    ratio = min(resp_len, truth_len) / max(resp_len, truth_len)

    return {
        "score": round(ratio, 4),
        "reason": f"Response: {resp_len} chars, Ground truth: {truth_len} chars"
    }


# Registry of built-in evaluators
BUILTIN_EVALUATORS = {
    "f1_score": {
        "name": "F1 Score",
        "description": "Harmonic mean of precision and recall in token overlaps between response and ground truth.",
        "fn": f1_score,
        "requires_ground_truth": True,
    },
    "bleu": {
        "name": "BLEU",
        "description": "Bilingual Evaluation Understudy score for n-gram overlap quality.",
        "fn": bleu_score,
        "requires_ground_truth": True,
    },
    "similarity": {
        "name": "Similarity",
        "description": "Jaccard similarity based on token overlap.",
        "fn": similarity_score,
        "requires_ground_truth": True,
    },
    "exact_match": {
        "name": "Exact Match",
        "description": "Binary score: 1.0 if response exactly matches ground truth.",
        "fn": exact_match,
        "requires_ground_truth": True,
    },
    "contains_match": {
        "name": "Contains Match",
        "description": "Binary score: 1.0 if ground truth is contained in response.",
        "fn": contains_match,
        "requires_ground_truth": True,
    },
    "length_ratio": {
        "name": "Length Ratio",
        "description": "Ratio of response length to ground truth length.",
        "fn": length_ratio,
        "requires_ground_truth": True,
    },
}


def run_builtin_evaluator(evaluator_id: str, response: str, ground_truth: str = "", **kwargs) -> Dict[str, Any]:
    """Run a built-in evaluator by ID."""
    if evaluator_id not in BUILTIN_EVALUATORS:
        return {"score": 0.0, "reason": f"Unknown evaluator: {evaluator_id}", "error": True}

    evaluator = BUILTIN_EVALUATORS[evaluator_id]
    try:
        result = evaluator["fn"](response, ground_truth, **kwargs)
        return result
    except Exception as e:
        return {"score": 0.0, "reason": f"Evaluator error: {str(e)}", "error": True}
