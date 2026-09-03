import json
from unittest.mock import Mock

from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
    InterviewQuestionPriority,
)
from app.services.ai_interview_question_generator import (
    AIInterviewQuestionGenerator,
)
from app.services.interview_focus_builder import (
    InterviewFocus,
)


def build_focus(
    competency: str = "Arquitetura",
) -> InterviewFocus:
    return InterviewFocus(
        competency=competency,
        category=(
            InterviewQuestionCategory.HARD_SKILL
        ),
        priority=(
            InterviewQuestionPriority.HIGH
        ),
        score=2,
        reason="Evidência limitada.",
        evidence_sources=set(),
    )


def build_response(
    competency: str = "Arquitetura",
):
    payload = {
        "questions": [
            {
                "category": "hard_skill",
                "competency": competency,
                "question": (
                    "Conte sobre uma decisão "
                    "arquitetural complexa que você "
                    "tomou."
                ),
                "reason": (
                    "Validar experiência prática."
                ),
                "priority": "high",
                "follow_up": (
                    "Quais trade-offs você avaliou?"
                ),
                "what_to_observe": [
                    "clareza técnica",
                    "trade-offs",
                    "autonomia",
                ],
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

    generator = AIInterviewQuestionGenerator(
        ai_client=ai_client
    )

    return generator, client


def test_returns_empty_set_when_no_focuses():
    generator, client = build_generator(
        build_response()
    )

    result = generator.generate([])

    assert result.questions == []

    client.responses.create.assert_not_called()


def test_generates_question():
    generator, client = build_generator(
        build_response()
    )

    result = generator.generate(
        [build_focus()]
    )

    assert len(result.questions) == 1

    question = result.questions[0]

    assert (
        question.competency
        == "Arquitetura"
    )

    assert (
        question.priority
        == InterviewQuestionPriority.HIGH
    )

    client.responses.create.assert_called_once()


def test_rejects_missing_question():
    response = Mock()
    response.output_text = json.dumps(
        {"questions": []}
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
            "exatamente uma pergunta"
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

    assert "Arquitetura" in user_message
    assert "Evidência limitada" in user_message
    assert '"score": 2' in user_message