import pytest
from pydantic import ValidationError

from app.schemas.risk_intelligence import (
    RiskAssessment,
    RiskCategory,
    RiskLevel,
)


def test_builds_risk_assessment():
    risk = RiskAssessment(
        title="DevOps requer validação",
        category=RiskCategory.EVIDENCE_GAP,
        level=RiskLevel.HIGH,
        description=(
            "Não foram encontradas evidências "
            "documentais suficientes."
        ),
        evidence=[],
        validation_question=(
            "Conte sobre sua experiência "
            "prática com DevOps."
        ),
        competency="DevOps",
    )

    assert risk.level == RiskLevel.HIGH

    assert (
        risk.category
        == RiskCategory.EVIDENCE_GAP
    )

    assert risk.evidence == []


def test_allows_null_validation_question():
    risk = RiskAssessment(
        title="Ponto de atenção",
        category=(
            RiskCategory.VALIDATION_REQUIRED
        ),
        level=RiskLevel.LOW,
        description="Validar durante entrevista.",
        evidence=[],
        validation_question=None,
        competency="DevOps",
    )

    assert risk.validation_question is None


def test_rejects_extra_fields():
    with pytest.raises(ValidationError):
        RiskAssessment(
            title="Teste",
            category=RiskCategory.OTHER,
            level=RiskLevel.MEDIUM,
            description="Teste",
            evidence=[],
            validation_question=None,
            invalid_field="x",
            competency="DevOps",
        )