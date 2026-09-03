from dataclasses import dataclass

from app.schemas.candidate_assessment import (
    CandidateAssessment,
    SkillAssessment,
    SkillType,
)
from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
    InterviewQuestionPriority,
)
from app.schemas.evidence import EvidenceSource


@dataclass
class InterviewFocus:
    competency: str
    category: InterviewQuestionCategory
    priority: InterviewQuestionPriority
    score: int
    reason: str
    evidence_sources: set[EvidenceSource]


class InterviewFocusBuilder:
    def build(
        self,
        assessment: CandidateAssessment,
    ) -> list[InterviewFocus]:
        focuses: list[InterviewFocus] = []

        focuses.extend(
            self._build_from_skills(
                assessment.hard_skills,
                InterviewQuestionCategory.HARD_SKILL,
            )
        )

        focuses.extend(
            self._build_from_skills(
                assessment.soft_skills,
                InterviewQuestionCategory.SOFT_SKILL,
            )
        )

        focuses.extend(
            self._build_from_skills(
                assessment.technologies,
                InterviewQuestionCategory.TECHNOLOGY,
            )
        )

        return self._sort(focuses)

    def _build_from_skills(
        self,
        skills: list[SkillAssessment],
        category: InterviewQuestionCategory,
    ) -> list[InterviewFocus]:
        focuses: list[InterviewFocus] = []

        for skill in skills:
            priority = self._priority_from_score(
                skill.score
            )

            focuses.append(
                InterviewFocus(
                    competency=skill.name,
                    category=category,
                    priority=priority,
                    score=skill.score,
                    reason=self._build_reason(
                        skill
                    ),
                    evidence_sources={
                        evidence.source
                        for evidence in skill.evidence
                    },
                )
            )

        return focuses

    @staticmethod
    def _priority_from_score(
        score: int,
    ) -> InterviewQuestionPriority:
        if score <= 2:
            return (
                InterviewQuestionPriority.HIGH
            )

        if score == 3:
            return (
                InterviewQuestionPriority.MEDIUM
            )

        return InterviewQuestionPriority.LOW

    @staticmethod
    def _build_reason(
        skill: SkillAssessment,
    ) -> str:
        if skill.score == 1:
            return (
                "Não há evidência documental "
                "suficiente para o requisito. "
                "A competência deve ser explorada "
                "durante a entrevista."
            )

        if skill.score == 2:
            return (
                "Há evidência limitada ou indireta. "
                "A entrevista deve buscar evidências "
                "práticas adicionais."
            )

        if skill.score == 3:
            return (
                "Há evidência compatível, mas ainda "
                "é necessário validar profundidade, "
                "contexto e nível de autonomia."
            )

        return (
            "Há evidência documental forte. "
            "A entrevista pode validar profundidade "
            "e consistência da experiência."
        )

    @staticmethod
    def _sort(
        focuses: list[InterviewFocus],
    ) -> list[InterviewFocus]:
        priority_order = {
            InterviewQuestionPriority.HIGH: 0,
            InterviewQuestionPriority.MEDIUM: 1,
            InterviewQuestionPriority.LOW: 2,
        }

        return sorted(
            focuses,
            key=lambda item: (
                priority_order[item.priority],
                item.category.value,
                item.competency.casefold(),
            ),
        )