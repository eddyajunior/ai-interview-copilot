from app.schemas.evidence import Evidence, EvidenceSource


def test_evidence_valid():
    evidence = Evidence(
        text="Implementação de microsserviços utilizando Kafka.",
        source=EvidenceSource.EXPERIENCE,
        source_reference="Senior Software Engineer - Empresa X",
        page=2,
    )

    assert evidence.text == "Implementação de microsserviços utilizando Kafka."
    assert evidence.source == EvidenceSource.EXPERIENCE
    assert evidence.page == 2