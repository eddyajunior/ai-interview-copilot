import json
from unittest.mock import Mock

from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
)
from app.schemas.risk_intelligence import (
    RiskCategory,
    RiskLevel,
)
from app.services.ai_risk_generator import (
    AIRiskGenerator,
)
from app.services.risk_focus_builder import (
    RiskFocus,
)


def build_focus(
    competency: str = "DevOps",
) -> RiskFocus:
    return RiskFocus(
        competency=competency,
        category=(
            InterviewQuestionCategory.HARD_SKILL
        ),
        level=RiskLevel.HIGH,
        risk_category=(
            RiskCategory.EVIDENCE_GAP
        ),
        score=1,
        description=(
            "Não foram encontradas evidências "
            "documentais suficientes."
        ),
    )


def build_response(
    competency: str = "DevOps",
):
    payload = {
        "risks": [
            {
                "competency": competency,
                "title": (
                    "DevOps requer validação"
                ),
                "category": "evidence_gap",
                "level": "high",
                "description": (
                    "Não há evidência documental "
                    "suficiente para confirmar "
                    "experiência prática com DevOps."
                ),
                "evidence": [],
                "validation_question": (
                    "Conte sobre uma situação em que "
                    "você aplicou práticas DevOps."
                ),
            }
        ]
    }

    response = Mock()
    response.output_text = json.dumps(
        payload,
        ensure_ascii=False,
    )

    return response


def build_generator(response):
    client = Mock()
    client.responses.create.return_value = response

    ai_client = Mock()
    ai_client.get_client.return_value = client

    generator = AIRiskGenerator(
        ai_client=ai_client
    )

    return generator, client


def test_returns_empty_list_when_no_focuses():
    generator, client = build_generator(
        build_response()
    )

    result = generator.generate([])

    assert result == []

    client.responses.create.assert_not_called()


def test_generates_risk():
    generator, client = build_generator(
        build_response()
    )

    result = generator.generate(
        [build_focus()]
    )

    assert len(result) == 1

    assert (
        result[0].competency
        == "DevOps"
    )

    assert (
        result[0].level
        == RiskLevel.HIGH
    )

    client.responses.create.assert_called_once()


def test_rejects_missing_risk():
    response = Mock()
    response.output_text = json.dumps(
        {"risks": []}
    )

    generator, _ = build_generator(
        response
    )

    try:
        generator.generate(
            [build_focus()]
        )

        assert False

    except ValueError as exc:
        assert (
            "exatamente um risco"
            in str(exc)
        )


def test_rejects_changed_competency():
    generator, _ = build_generator(
        build_response(
            competency="Outra competência"
        )
    )

    try:
        generator.generate(
            [build_focus()]
        )

        assert False

    except ValueError as exc:
        assert (
            "não correspondem exatamente"
            in str(exc)
        )


def test_prompt_contains_focus_context():
    generator, client = build_generator(
        build_response()
    )

    generator.generate(
        [build_focus()]
    )

    call = (
        client.responses.create
        .call_args.kwargs
    )

    user_message = call["input"][1][
        "content"
    ]

    assert "DevOps" in user_message
    assert '"score": 1' in user_message
    assert "evidence_gap" in user_message