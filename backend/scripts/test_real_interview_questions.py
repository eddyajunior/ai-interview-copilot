from pathlib import Path

from app.services.ai_interview_question_generator import (
    AIInterviewQuestionGenerator,
)
from app.services.ai_job_analyzer import AIJobAnalyzer
from app.services.ai_resume_analyzer import AIResumeAnalyzer
from app.services.candidate_scorer import CandidateScorer
from app.services.document_parser import DocumentParser
from app.services.interview_focus_builder import (
    InterviewFocusBuilder,
)
from app.services.interview_focus_selector import (
    InterviewFocusSelector,
)
from app.services.interview_intelligence_service import (
    InterviewIntelligenceService,
)
from app.services.risk_intelligence_service import (
    RiskIntelligenceService,
)
from app.services.assessment_summary_service import (
    AssessmentSummaryService,
)

BASE_DIR = Path(__file__).resolve().parents[1]

JOB_FILE = BASE_DIR / "data" / "vaga.txt"
RESUME_FILE = BASE_DIR / "data" / "curriculo.pdf"


def main():
    parser = DocumentParser()

    print("\n=== CARREGANDO DOCUMENTOS ===")

    job_document = parser.parse(JOB_FILE)
    resume_document = parser.parse(RESUME_FILE)

    print(f"Vaga: {JOB_FILE.name}")
    print(f"Currículo: {RESUME_FILE.name}")

    print("\n=== ANALISANDO VAGA ===")

    job_profile = AIJobAnalyzer().analyze(
        job_document
    )

    print(f"Cargo: {job_profile.title}")

    print("\n=== ANALISANDO CURRÍCULO ===")

    resume_profile = AIResumeAnalyzer().analyze(
        resume_document
    )

    print(
        "Candidato:",
        resume_profile.candidate_name,
    )

    print("\n=== GERANDO ASSESSMENT ===")

    assessment = CandidateScorer().build_candidate_assessment(
        job_profile,
        resume_profile,
    )

    assessment = InterviewIntelligenceService().enrich(
        assessment
    )

    assessment = RiskIntelligenceService().enrich(
        assessment
    )

    assessment = AssessmentSummaryService().enrich(
        assessment
    )

    print(
        "\n=== PONTOS DE ATENÇÃO NO CANDIDATE ASSESSMENT ==="
    )

    print(
        f"Riscos integrados: "
        f"{len(assessment.risks)}"
    )

    for index, risk in enumerate(
        assessment.risks,
        start=1,
    ):
        print("\n" + "=" * 70)

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

    print(
        "Aderência documental:",
        f"{assessment.adherence_percentage:.2f}%",
    )

    print("\n=== CONSTRUINDO FOCOS ===")

    focuses = InterviewFocusBuilder().build(
        assessment
    )

    print(
        f"Focos disponíveis: {len(focuses)}"
    )

    print("\n=== SELECIONANDO FOCOS ===")

    selected_focuses = (
        InterviewFocusSelector()
        .select(focuses)
    )

    print(
        f"Focos selecionados: "
        f"{len(selected_focuses)}"
    )

    for index, focus in enumerate(
        selected_focuses,
        start=1,
    ):
        print(
            f"{index}. "
            f"[{focus.priority.value.upper()}] "
            f"[{focus.category.value}] "
            f"{focus.competency} "
            f"(score {focus.score}/5)"
        )

    print(
        "\n=== GERANDO PERGUNTAS COM IA ==="
    )

    question_set = (
        AIInterviewQuestionGenerator()
        .generate(selected_focuses)
    )

    # print(
    #     f"\nPerguntas geradas: "
    #     f"{len(question_set.questions)}"
    # )

    # for index, question in enumerate(
    #     question_set.questions,
    #     start=1,
    # ):
    #     print("\n" + "=" * 70)

    #     print(
    #         f"{index}. "
    #         f"[{question.priority.value.upper()}] "
    #         f"[{question.category.value}]"
    #     )

    #     print(
    #         f"Competência: "
    #         f"{question.competency}"
    #     )

    #     print(
    #         f"Pergunta: "
    #         f"{question.question}"
    #     )

    #     print(
    #         f"Motivo: "
    #         f"{question.reason}"
    #     )

    #     print(
    #         f"Follow-up: "
    #         f"{question.follow_up}"
    #     )

    #     print("Observar:")

    #     for item in question.what_to_observe:
    #         print(f"  - {item}")

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
        print("\n" + "=" * 70)

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
            print(f"  - {item}")
            
    print("\n" + "=" * 70)

    print(
        "\n=== TESTE REAL CONCLUÍDO ==="
    )

    print(
        "\n=== COMENTÁRIOS PARA O ENTREVISTADOR ==="
    )

    for index, comment in enumerate(
        assessment.interviewer_comments,
        start=1,
    ):
        print(
            f"{index}. {comment}"
        )

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


if __name__ == "__main__":
    main()

