from app.schemas.evidence import (
    Evidence,
    EvidenceSource,
)
from app.schemas.requirement_match import (
    MatchType,
    RequirementMatch,
    RequirementMatchSet,
)


def test_creates_semantic_requirement_match():
    match = RequirementMatch(
        requirement_name="Cloud e FinOps",
        matched_skill_names=[
            "FinOps",
            "AWS",
        ],
        match_type=MatchType.SEMANTIC,
        evidences=[
            Evidence(
                text="Atuação com FinOps em ambiente AWS.",
                source=EvidenceSource.EXPERIENCE,
                source_reference="Empresa X",
                page=1,
            )
        ],
        justification=(
            "FinOps e AWS possuem relação direta "
            "com o requisito da vaga."
        ),
    )

    assert match.requirement_name == "Cloud e FinOps"
    assert match.match_type == MatchType.SEMANTIC
    assert len(match.evidences) == 1


def test_creates_requirement_without_match():
    match = RequirementMatch(
        requirement_name="Low-code",
        matched_skill_names=[],
        match_type=MatchType.NONE,
        evidences=[],
        justification=(
            "Nenhuma evidência relacionada foi encontrada."
        ),
    )

    assert match.match_type == MatchType.NONE
    assert match.evidences == []


def test_creates_requirement_match_set():
    match_set = RequirementMatchSet(
        matches=[
            RequirementMatch(
                requirement_name="Arquitetura de software",
                matched_skill_names=[
                    "Arquitetura de software",
                ],
                match_type=MatchType.EXACT,
                evidences=[],
                justification="Correspondência direta.",
            )
        ]
    )

    assert len(match_set.matches) == 1