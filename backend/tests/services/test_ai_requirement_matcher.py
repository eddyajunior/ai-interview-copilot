import json

from app.schemas.evidence import (
    Evidence,
    EvidenceSource,
)
from app.schemas.job_profile import (
    JobRequirement,
    RequirementImportance,
)
from app.schemas.requirement_match import (
    MatchType,
)
from app.schemas.resume_profile import (
    ResumeProfile,
    ResumeSkillEvidence,
)
from app.services.ai_requirement_matcher import (
    AIRequirementMatcher,
)


class FakeResponse:
    def __init__(self, output_text: str):
        self.output_text = output_text


class FakeResponses:
    def __init__(self, output_text: str):
        self.output_text = output_text

    def create(self, **kwargs):
        return FakeResponse(
            self.output_text
        )


class FakeOpenAI:
    def __init__(self, output_text: str):
        self.responses = FakeResponses(
            output_text
        )


class FakeAIClient:
    def __init__(self, output_text: str):
        self.client = FakeOpenAI(
            output_text
        )

    def get_client(self):
        return self.client


def build_resume():
    return ResumeProfile(
        candidate_name="Candidate",
        professional_summary=None,
        experiences=[],
        education=[],
        certifications=[],
        hard_skills=[
            ResumeSkillEvidence(
                skill="FinOps",
                evidence=[
                    Evidence(
                        text="Atuação com FinOps em AWS.",
                        source=EvidenceSource.EXPERIENCE,
                        source_reference="Empresa X",
                        page=1,
                    )
                ],
            )
        ],
        soft_skill_evidences=[],
        technologies=[
            ResumeSkillEvidence(
                skill="AWS",
                evidence=[
                    Evidence(
                        text="Ambientes AWS.",
                        source=EvidenceSource.EXPERIENCE,
                        source_reference="Empresa X",
                        page=1,
                    )
                ],
            )
        ],
        leadership_evidences=[],
        measurable_results=[],
    )


def test_matches_requirement_using_structured_output():
    output = {
        "matches": [
            {
                "requirement_name": "Cloud e FinOps",
                "matched_skill_names": [
                    "FinOps",
                    "AWS",
                ],
                "match_type": "semantic",
                "evidences": [
                    {
                        "text": "Atuação com FinOps em AWS.",
                        "source": "experience",
                        "source_reference": "Empresa X",
                        "page": 1,
                    }
                ],
                "justification": (
                    "FinOps e AWS sustentam o requisito."
                ),
            }
        ]
    }

    matcher = AIRequirementMatcher(
        ai_client=FakeAIClient(
            json.dumps(output)
        )
    )

    result = matcher.match(
        requirements=[
            JobRequirement(
                name="Cloud e FinOps",
                importance=RequirementImportance.REQUIRED,
                description=None,
            )
        ],
        resume=build_resume(),
    )

    assert len(result.matches) == 1

    match = result.matches[0]

    assert (
        match.requirement_name
        == "Cloud e FinOps"
    )

    assert match.match_type == MatchType.SEMANTIC

    assert match.matched_skill_names == [
        "FinOps",
        "AWS",
    ]

    assert len(match.evidences) == 1


def test_returns_empty_set_when_no_requirements():
    matcher = AIRequirementMatcher(
        ai_client=FakeAIClient("{}")
    )

    result = matcher.match(
        requirements=[],
        resume=build_resume(),
    )

    assert result.matches == []


def test_rejects_missing_requirement_in_response():
    output = {
        "matches": []
    }

    matcher = AIRequirementMatcher(
        ai_client=FakeAIClient(
            json.dumps(output)
        )
    )

    try:
        matcher.match(
            requirements=[
                JobRequirement(
                    name="Cloud e FinOps",
                    importance=RequirementImportance.REQUIRED,
                    description=None,
                )
            ],
            resume=build_resume(),
        )

        assert False

    except ValueError as exc:
        assert (
            "exatamente uma"
            in str(exc)
        )


def test_rejects_different_requirement_name():
    output = {
        "matches": [
            {
                "requirement_name": "Outro requisito",
                "matched_skill_names": [],
                "match_type": "none",
                "evidences": [],
                "justification": (
                    "Nenhuma evidência encontrada."
                ),
            }
        ]
    }

    matcher = AIRequirementMatcher(
        ai_client=FakeAIClient(
            json.dumps(output)
        )
    )

    try:
        matcher.match(
            requirements=[
                JobRequirement(
                    name="Cloud e FinOps",
                    importance=RequirementImportance.REQUIRED,
                    description=None,
                )
            ],
            resume=build_resume(),
        )

        assert False

    except ValueError as exc:
        assert (
            "não correspondem"
            in str(exc)
        )

def test_rejects_evidence_not_present_in_catalog():
    output = {
        "matches": [
            {
                "requirement_name": "Cloud e FinOps",
                "matched_skill_names": [
                    "FinOps"
                ],
                "match_type": "semantic",
                "evidences": [
                    {
                        "text": (
                            "Texto criado pela IA "
                            "e inexistente no currículo."
                        ),
                        "source": "experience",
                        "source_reference": "Empresa X",
                        "page": 1,
                    }
                ],
                "justification": (
                    "A evidência sustentaria "
                    "o requisito."
                ),
            }
        ]
    }

    matcher = AIRequirementMatcher(
        ai_client=FakeAIClient(
            json.dumps(output)
        )
    )

    try:
        matcher.match(
            requirements=[
                JobRequirement(
                    name="Cloud e FinOps",
                    importance=(
                        RequirementImportance.REQUIRED
                    ),
                    description=None,
                )
            ],
            resume=build_resume(),
        )

        assert False

    except ValueError as exc:
        assert (
            "não existe no catálogo"
            in str(exc)
        )