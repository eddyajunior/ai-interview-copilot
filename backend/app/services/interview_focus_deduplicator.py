import re
import unicodedata

from app.schemas.interview_intelligence import (
    InterviewQuestionPriority,
)
from app.services.interview_focus_builder import (
    InterviewFocus,
)


class InterviewFocusDeduplicator:
    STOP_WORDS = {
        "a",
        "as",
        "com",
        "da",
        "das",
        "de",
        "do",
        "dos",
        "e",
        "em",
        "para",
    }

    PRIORITY_ORDER = {
        InterviewQuestionPriority.HIGH: 0,
        InterviewQuestionPriority.MEDIUM: 1,
        InterviewQuestionPriority.LOW: 2,
    }

    def deduplicate(
        self,
        focuses: list[InterviewFocus],
    ) -> list[InterviewFocus]:
        ordered = sorted(
            focuses,
            key=lambda focus: (
                self.PRIORITY_ORDER[
                    focus.priority
                ],
                focus.score,
            ),
        )

        selected: list[InterviewFocus] = []

        for candidate in ordered:
            if any(
                self._is_redundant(
                    candidate,
                    existing,
                )
                for existing in selected
            ):
                continue

            selected.append(candidate)

        return selected

    def _is_redundant(
        self,
        first: InterviewFocus,
        second: InterviewFocus,
    ) -> bool:
        first_terms = self._terms(
            first.competency
        )
        second_terms = self._terms(
            second.competency
        )

        if not first_terms or not second_terms:
            return False

        intersection = (
            first_terms & second_terms
        )

        smaller_size = min(
            len(first_terms),
            len(second_terms),
        )

        overlap = (
            len(intersection)
            / smaller_size
        )

        return overlap >= 0.75

    def _terms(
        self,
        value: str,
    ) -> set[str]:
        normalized = unicodedata.normalize(
            "NFKD",
            value,
        )

        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(
                character
            )
        )

        normalized = normalized.casefold()

        tokens = re.findall(
            r"[a-z0-9]+",
            normalized,
        )

        return {
            self._singularize(token)
            for token in tokens
            if token not in self.STOP_WORDS
        }

    @staticmethod
    def _singularize(
        token: str,
    ) -> str:
        if (
            len(token) > 4
            and token.endswith("s")
        ):
            return token[:-1]

        return token