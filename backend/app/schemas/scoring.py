from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SkillScore(int, Enum):
    NOT_EVIDENCED = 1
    LIMITED = 2
    COMPATIBLE = 3
    STRONG = 4
    VERY_STRONG = 5


class AssessmentStatus(str, Enum):
    NOT_EVIDENCED = "not_evidenced"
    NEEDS_VALIDATION = "needs_validation"
    COMPATIBLE = "compatible"
    STRONG = "strong"


class EvidenceStrength(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ScoringRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: SkillScore
    evidence_strength: EvidenceStrength
    status: AssessmentStatus
    description: str


SCORING_RULES = {
    SkillScore.NOT_EVIDENCED: ScoringRule(
        score=SkillScore.NOT_EVIDENCED,
        evidence_strength=EvidenceStrength.NONE,
        status=AssessmentStatus.NOT_EVIDENCED,
        description=(
            "Nenhuma evidência relevante encontrada no currículo. "
            "Isso não significa ausência da competência."
        ),
    ),
    SkillScore.LIMITED: ScoringRule(
        score=SkillScore.LIMITED,
        evidence_strength=EvidenceStrength.LOW,
        status=AssessmentStatus.NEEDS_VALIDATION,
        description=(
            "Existe evidência limitada, indireta ou pouco detalhada. "
            "A competência deve ser aprofundada na entrevista."
        ),
    ),
    SkillScore.COMPATIBLE: ScoringRule(
        score=SkillScore.COMPATIBLE,
        evidence_strength=EvidenceStrength.MEDIUM,
        status=AssessmentStatus.COMPATIBLE,
        description=(
            "Existem evidências compatíveis com o requisito da vaga."
        ),
    ),
    SkillScore.STRONG: ScoringRule(
        score=SkillScore.STRONG,
        evidence_strength=EvidenceStrength.HIGH,
        status=AssessmentStatus.STRONG,
        description=(
            "Existem evidências consistentes, relevantes e diretamente "
            "relacionadas ao requisito."
        ),
    ),
    SkillScore.VERY_STRONG: ScoringRule(
        score=SkillScore.VERY_STRONG,
        evidence_strength=EvidenceStrength.HIGH,
        status=AssessmentStatus.STRONG,
        description=(
            "Existem múltiplas evidências fortes, recorrentes ou acompanhadas "
            "de resultados relevantes diretamente relacionados ao requisito."
        ),
    ),
}