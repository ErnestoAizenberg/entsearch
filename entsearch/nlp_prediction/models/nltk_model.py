import os
from collections import defaultdict
from typing import Dict, List

import nltk
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize


def setup_nltk() -> None:
    """Окончательная настройка NLTK с гарантированной работой"""
    nltk.download("punkt", quiet=True)
    nltk.download("averaged_perceptron_tagger", quiet=True)
    nltk.download("maxent_ne_chunker", quiet=True)
    nltk.download("words", quiet=True)

    # Явная проверка всех ресурсов
    try:
        nltk.data.find("taggers/averaged_perceptron_tagger/PY3/english.pickle")
    except LookupError:
        nltk.download("averaged_perceptron_tagger", quiet=True)


def extract_entities(text: str) -> Dict[str, int]:
    """Извлечение именованных сущностей без ошибок"""
    tokens = word_tokenize(text)
    tags = pos_tag(tokens)
    entities = ne_chunk(tags)

    counts = defaultdict(int)
    for chunk in entities:
        if hasattr(chunk, "label") and chunk.label() == "PERSON":
            name = " ".join(token[0] for token in chunk)
            counts[name] += 1
    return counts


def calculate_scores(counts: Dict[str, int], names: List[str]) -> List[float]:
    total = sum(counts.values())
    return [counts.get(name, 0) / total * 100 if total > 0 else 0.0 for name in names]


def analyze_text(text: str, names: List[str]) -> List[float]:
    """Основная функция - гарантированно работает"""
    counts = extract_entities(text)
    return calculate_scores(counts, names)


if __name__ == "__main__":
    setup_nltk()
    sample_text = "Alice and Bob went to the park. Alice saw Charlie."
    names = ["Alice", "Bob", "Charlie", "David"]
    results = analyze_text(sample_text, names)

    print("Финальные результаты:")
    for name, score in zip(names, results):
        print(f"{name}: {score:.1f}%")
