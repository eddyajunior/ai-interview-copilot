from dataclasses import dataclass

from app.schemas.candidate_assessment import (
    CandidateAssessment,
    SkillAssessment,
)
from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
)
from app.schemas.risk_intelligence import (
    RiskCategory,
    RiskLevel,
)


@dataclass
class RiskFocus:
    competency: str
    category: InterviewQuestionCategory
    level: RiskLevel
    risk_category: RiskCategory
    score: int
    description: str


class RiskFocusBuilder:
    def build(
        self,
        assessment: CandidateAssessment,
    ) -> list[RiskFocus]:
        focuses: list[RiskFocus] = []

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
    ) -> list[RiskFocus]:
        focuses: list[RiskFocus] = []

        for skill in skills:
            focus = self._build_focus(
                skill,
                category,
            )

            if focus is not None:
                focuses.append(focus)

        return focuses

    def _build_focus(
        self,
        skill: SkillAssessment,
        category: InterviewQuestionCategory,
    ) -> RiskFocus | None:
        if skill.score == 1:
            return RiskFocus(
                competency=skill.name,
                category=category,
                level=RiskLevel.HIGH,
                risk_category=(
                    RiskCategory.EVIDENCE_GAP
                ),
                score=skill.score,
                description=(
                    "Não foram encontradas evidências "
                    "documentais suficientes para este "
                    "requisito. Isso não significa ausência "
                    "da competência e deve ser validado "
                    "durante a entrevista."
                ),
            )

        if skill.score == 2:
            return RiskFocus(
                competency=skill.name,
                category=category,
                level=RiskLevel.MEDIUM,
                risk_category=(
                    RiskCategory.LIMITED_EVIDENCE
                ),
                score=skill.score,
                description=(
                    "Foram encontradas evidências limitadas "
                    "ou indiretas para este requisito. "
                    "É necessária validação adicional."
                ),
            )

        return None

    @staticmethod
    def _sort(
        focuses: list[RiskFocus],
    ) -> list[RiskFocus]:
        order = {
            RiskLevel.HIGH: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.LOW: 2,
        }

        return sorted(
            focuses,
            key=lambda item: (
                order[item.level],
                item.category.value,
                item.competency.casefold(),
            ),
        )