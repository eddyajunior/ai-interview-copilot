from pathlib import Path

from app.services.assessment_orchestrator import (
    AssessmentOrchestrator,
)
from app.services.document_parser import DocumentParser


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

JOB_FILE = DATA_DIR / "vaga.txt"
RESUME_FILE = DATA_DIR / "curriculo.pdf"


def print_separator() -> None:
    print("\n" + "=" * 70)


def print_questions(assessment) -> None:
    print(
        "\n=== PERGUNTAS NO CANDIDATE ASSESSMENT ==="
    )

    print(
        f"Perguntas integradas: "
        f"{len(assessment.questions)}"
    )

    for index, question in enumerate(
        assessment.questions,
        start=1,
    ):
        print_separator()

        print(
            f"{index}. "
            f"[{question.priority.value.upper()}] "
            f"[{question.category.value}]"
        )

        print(
            f"Competência: "
            f"{question.competency}"
        )

        print(
            f"Pergunta: "
            f"{question.question}"
        )

        print(
            f"Motivo: "
            f"{question.reason}"
        )

        print(
            f"Follow-up: "
            f"{question.follow_up}"
        )

        print("Observar:")

        for item in question.what_to_observe:
            print(
                f"  - {item}"
            )


def print_risks(assessment) -> None:
    print(
        "\n=== PONTOS DE ATENÇÃO NO "
        "CANDIDATE ASSESSMENT ==="
    )

    print(
        f"Riscos integrados: "
        f"{len(assessment.risks)}"
    )

    for index, risk in enumerate(
        assessment.risks,
        start=1,
    ):
        print_separator()

        print(
            f"{index}. "
            f"[{risk.level.value.upper()}] "
            f"[{risk.category.value}]"
        )

        print(
            f"Competência: "
            f"{risk.competency}"
        )

        print(
            f"Título: "
            f"{risk.title}"
        )

        print(
            f"Descrição: "
            f"{risk.description}"
        )

        print(
            f"Pergunta de validação: "
            f"{risk.validation_question}"
        )


def print_interviewer_comments(
    assessment,
) -> None:
    print(
        "\n=== COMENTÁRIOS PARA O ENTREVISTADOR ==="
    )

    if not assessment.interviewer_comments:
        print(
            "Nenhum comentário gerado."
        )
        return

    for index, comment in enumerate(
        assessment.interviewer_comments,
        start=1,
    ):
        print(
            f"{index}. {comment}"
        )


def print_recommendation(
    assessment,
) -> None:
    print(
        "\n=== RECOMENDAÇÕES ==="
    )

    print(
        f"Curto prazo: "
        f"{assessment.recommendation.short_term}"
    )

    print(
        f"Médio prazo: "
        f"{assessment.recommendation.medium_term}"
    )

    print(
        f"Longo prazo: "
        f"{assessment.recommendation.long_term}"
    )


def main() -> None:
    print(
        "\n=== CARREGANDO DOCUMENTOS ==="
    )

    print(
        f"Vaga: {JOB_FILE.name}"
    )

    print(
        f"Currículo: {RESUME_FILE.name}"
    )

    if not JOB_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo da vaga não encontrado: "
            f"{JOB_FILE}"
        )

    if not RESUME_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo do currículo não encontrado: "
            f"{RESUME_FILE}"
        )

    parser = DocumentParser()

    job_document = parser.parse(
        JOB_FILE
    )

    resume_document = parser.parse(
        RESUME_FILE
    )

    print(
        "\n=== GERANDO ASSESSMENT "
        "COM ORQUESTRADOR ==="
    )

    orchestrator = AssessmentOrchestrator()

    assessment = orchestrator.execute(
        job_document,
        resume_document,
    )

    print(
        "\n=== ASSESSMENT GERADO ==="
    )

    print(
        f"Candidato: "
        f"{assessment.candidate_name}"
    )

    print(
        f"Vaga: "
        f"{assessment.job_title}"
    )

    print(
        f"Aderência documental: "
        f"{assessment.adherence_percentage:.2f}%"
    )

    print_questions(
        assessment
    )

    print_risks(
        assessment
    )

    print_interviewer_comments(
        assessment
    )

    print_recommendation(
        assessment
    )

    print_separator()

    print(
        "\n=== TESTE REAL DO "
        "ASSESSMENT ORCHESTRATOR CONCLUÍDO ==="
    )


if __name__ == "__main__":
    main()