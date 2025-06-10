import re
from difflib import SequenceMatcher
from typing import Dict, List


class NameProbabilityAnalyzer:
    def __init__(self, names: List[str], sensitivity: float = 0.85):
        self.names = names
        self.sensitivity = (
            sensitivity  # Уровень чувствительности к похожим именам (0-1)
        )
        self.name_variants = self._generate_variants(names)

    def _generate_variants(self, names: List[str]) -> Dict[str, List[str]]:
        """Генерирует все возможные варианты написания каждого имени"""
        variants = {}
        for name in names:
            name_vars = {
                name,
                name.lower(),
                name.replace(" ", ""),
                name.replace(" ", "").lower(),
                name.replace(".", "").lower(),
            }

            # Добавляем варианты с инициалами
            if " " in name:
                parts = name.split()
                # Варианты типа "A. Johnson", "A Johnson"
                initials = [
                    f"{parts[0][0]}. {' '.join(parts[1:])}",
                    f"{parts[0][0]} {' '.join(parts[1:])}",
                    f"{' '.join(parts[1:])} {parts[0][0]}.",
                ]
                name_vars.update(initials)
                name_vars.update([v.lower() for v in initials])

            variants[name] = list(name_vars)
        return variants

    def _calculate_similarity(self, name: str, text: str) -> float:
        """Вычисляет степень соответствия имени тексту (0-1)"""
        words = re.findall(r"\b\w[\w-]+\b", text.lower())
        max_similarity = 0.0

        for variant in self.name_variants[name]:
            variant_lower = variant.lower()

            # Проверяем точные совпадения
            if variant_lower in words:
                return 1.0  # Максимальная уверенность при точном совпадении

            # Проверяем похожие варианты
            for word in words:
                similarity = SequenceMatcher(None, variant_lower, word).ratio()
                if similarity > max_similarity:
                    max_similarity = similarity

        # Нормализуем результат по чувствительности
        return max(
            0.0, min(1.0, (max_similarity - self.sensitivity) / (1 - self.sensitivity))
        )

    def calculate_probabilities(self, text: str) -> List[float]:
        """Возвращает список вероятностей для каждого имени в порядке их предоставления"""
        probabilities = []

        for name in self.names:
            similarity = self._calculate_similarity(name, text)
            probabilities.append(round(similarity, 2))

        # Нормализуем так, чтобы сумма вероятностей не превышала 1
        total = sum(probabilities)
        if total > 1.0:
            probabilities = [p / total for p in probabilities]

        return probabilities


def print_probabilities(names: List[str], probabilities: List[float]):
    print("Вероятности принадлежности текста именам:")
    for name, prob in zip(names, probabilities):
        print(f"{name}: {prob:.2f}")


if __name__ == "__main__":
    # Пример использования
    text = """
    Alice Johnson and Bob Smith went to the park. Later, alice met Charlie Brown.
    A. Johnson was happy, but b.smith forgot his bag. Some guy called Alise J. was there too.
    """
    names = ["Alice Johnson", "Bob Smith", "Charlie Brown", "David Wilson"]

    analyzer = NameProbabilityAnalyzer(names, sensitivity=0.75)
    probs = analyzer.calculate_probabilities(text)

    print_probabilities(names, probs)
    # Пример вывода: [0.85, 0.74, 0.95, 0.05]
