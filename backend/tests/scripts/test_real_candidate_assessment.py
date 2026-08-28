from pathlib import Path

from app.services.ai_job_analyzer import AIJobAnalyzer
from app.services.ai_resume_analyzer import AIResumeAnalyzer
from app.services.candidate_scorer import CandidateScorer
from app.services.document_parser import DocumentParser


BASE_DIR = Path(__file__).resolve().parents[1]


def main():
    job_path = BASE_DIR / "vaga.txt"
    resume_path = BASE_DIR / "curriculo.pdf"

    if not job_path.exists():
        raise FileNotFoundError(
            f"Arquivo da vaga não encontrado: {job_path}"
        )

    if not resume_path.exists():
        raise FileNotFoundError(
            f"Currículo não encontrado: {resume_path}"
        )

    parser = DocumentParser()

    job_document = parser.parse(job_path)
    resume_document = parser.parse(resume_path)

    print("\n1. Analisando vaga...")
    job_profile = AIJobAnalyzer().analyze(
        job_document.content
    )

    print("Vaga:", job_profile.title)
    print("Senioridade:", job_profile.seniority)

    print("\n2. Analisando currículo...")
    resume_profile = AIResumeAnalyzer().analyze(
        resume_document
    )

    print(
        "Candidato:",
        resume_profile.candidate_name,
    )

    print("\n3. Calculando assessment...")
    assessment = CandidateScorer().build_candidate_assessment(
        job_profile,
        resume_profile,
    )

    print("\n" + "=" * 70)
    print("CANDIDATE ASSESSMENT")
    print("=" * 70)

    print(
        f"\nAderência documental: "
        f"{assessment.adherence_percentage:.2f}%"
    )

    print("\nResumo:")
    print(assessment.summary)

    print("\n--- HARD SKILLS ---")
    for skill in assessment.hard_skills:
        print(
            f"{skill.name}: "
            f"{skill.score}/5 "
            f"[{skill.status}] "
            f"confidence={skill.confidence}"
        )
        print(
            f"  {skill.justification}"
        )

    print("\n--- TECHNOLOGIES ---")
    for skill in assessment.technologies:
        print(
            f"{skill.name}: "
            f"{skill.score}/5 "
            f"[{skill.status}] "
            f"confidence={skill.confidence}"
        )
        print(
            f"  {skill.justification}"
        )

    print("\n--- SOFT SKILLS ---")
    for skill in assessment.soft_skills:
        print(
            f"{skill.name}: "
            f"{skill.score}/5 "
            f"[{skill.status}] "
            f"confidence={skill.confidence}"
        )
        print(
            f"  {skill.justification}"
        )

    print("\n--- STRENGTHS ---")
    if assessment.strengths:
        for strength in assessment.strengths:
            print("-", strength)
    else:
        print("Nenhuma força documental classificada como forte.")

    print("\n--- GAPS DE EVIDÊNCIA ---")
    if assessment.weaknesses:
        for weakness in assessment.weaknesses:
            print("-", weakness)
    else:
        print("Nenhum gap documental relevante identificado.")

    print("\n--- RECOMENDAÇÃO ---")
    print(
        "Curto prazo:",
        assessment.recommendation.short_term,
    )
    print(
        "Médio prazo:",
        assessment.recommendation.medium_term,
    )
    print(
        "Longo prazo:",
        assessment.recommendation.long_term,
    )


if __name__ == "__main__":
    main()