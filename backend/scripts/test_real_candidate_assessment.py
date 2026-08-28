from pathlib import Path

from app.services.ai_job_analyzer import AIJobAnalyzer
from app.services.ai_resume_analyzer import AIResumeAnalyzer
from app.services.candidate_scorer import CandidateScorer
from app.services.document_parser import DocumentParser


BASE_DIR = Path(__file__).resolve().parents[1]


def print_job_profile(job_profile) -> None:
    print()
    print("=" * 70)
    print("JOB PROFILE EXTRAÍDO")
    print("=" * 70)

    print("\nHARD SKILLS:")
    for item in job_profile.hard_skills:
        print(
            f"- {item.name} "
            f"[{item.importance.value}]"
        )

    print("\nTECHNOLOGIES:")
    for item in job_profile.technologies:
        print(
            f"- {item.name} "
            f"[{item.importance.value}]"
        )

    print("\nSOFT SKILLS:")
    for item in job_profile.soft_skills:
        print(
            f"- {item.name} "
            f"[{item.importance.value}]"
        )

    total_requirements = (
        len(job_profile.hard_skills)
        + len(job_profile.technologies)
        + len(job_profile.soft_skills)
    )

    print(
        "\nTOTAL DE REQUISITOS APÓS "
        f"NORMALIZAÇÃO: {total_requirements}"
    )

    print("=" * 70)


def print_skill_group(
    title: str,
    skills,
) -> None:
    print(f"\n--- {title} ---")

    if not skills:
        print("Nenhum item.")
        return

    for skill in skills:
        print(
            f"{skill.name}: "
            f"{skill.score}/5 "
            f"[{skill.status}] "
            f"confidence={skill.confidence}"
        )

        print(
            f"  {skill.justification}"
        )


def print_list(
    title: str,
    items: list[str],
) -> None:
    print(f"\n--- {title} ---")

    if not items:
        print("- Nenhum item.")
        return

    for item in items:
        print(f"- {item}")


def main() -> None:
    parser = DocumentParser()

    job_path = (
        BASE_DIR
        / "data"
        / "vaga.txt"
    )

    resume_path = (
        BASE_DIR
        / "data"
        / "curriculo.pdf"
    )

    if not job_path.exists():
        raise FileNotFoundError(
            "Arquivo da vaga não encontrado: "
            f"{job_path}"
        )

    if not resume_path.exists():
        raise FileNotFoundError(
            "Arquivo do currículo não encontrado: "
            f"{resume_path}"
        )

    print("1. Analisando vaga...")

    job_document = parser.parse(
        job_path
    )

    job_profile = (
        AIJobAnalyzer()
        .analyze(job_document)
    )

    
    print(
        f"Vaga: {job_profile.title}"
    )

    print(
        f"Senioridade: "
        f"{job_profile.seniority}"
    )

    print_job_profile(
        job_profile
    )

    print("\n2. Analisando currículo...")

    resume_document = parser.parse(
        resume_path
    )

    resume_profile = (
        AIResumeAnalyzer()
        .analyze(resume_document)
    )

    print(
        f"Candidato: "
        f"{resume_profile.candidate_name}"
    )

    print(
        "\n3. Calculando assessment..."
    )

    assessment = (
        CandidateScorer()
        .build_candidate_assessment(
            job_profile,
            resume_profile,
        )
    )

    print()
    print("=" * 70)
    print("CANDIDATE ASSESSMENT")
    print("=" * 70)

    print(
        "\nAderência documental: "
        f"{assessment.adherence_percentage:.2f}%"
    )

    print("\nResumo:")
    print(
        assessment.summary
    )

    print_skill_group(
        "HARD SKILLS",
        assessment.hard_skills,
    )

    print_skill_group(
        "TECHNOLOGIES",
        assessment.technologies,
    )

    print_skill_group(
        "SOFT SKILLS",
        assessment.soft_skills,
    )

    print_list(
        "STRENGTHS",
        assessment.strengths,
    )

    print_list(
        "GAPS DE EVIDÊNCIA",
        assessment.weaknesses,
    )

    print("\n--- RECOMENDAÇÃO ---")

    print(
        "Curto prazo: "
        f"{assessment.recommendation.short_term}"
    )

    print(
        "Médio prazo: "
        f"{assessment.recommendation.medium_term}"
    )

    print(
        "Longo prazo: "
        f"{assessment.recommendation.long_term}"
    )


if __name__ == "__main__":
    main()