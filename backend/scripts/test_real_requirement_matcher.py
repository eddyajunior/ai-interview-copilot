from pathlib import Path

from app.services.ai_job_analyzer import AIJobAnalyzer
from app.services.ai_requirement_matcher import AIRequirementMatcher
from app.services.ai_resume_analyzer import AIResumeAnalyzer
from app.services.document_parser import DocumentParser


BASE_DIR = Path(__file__).resolve().parents[1]


def print_matches(title, match_set):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    for match in match_set.matches:
        print(f"\nRequisito: {match.requirement_name}")
        print(f"Match type: {match.match_type.value}")

        if match.matched_skill_names:
            print(
                "Skills relacionadas:",
                ", ".join(match.matched_skill_names),
            )
        else:
            print("Skills relacionadas: nenhuma")

        print("Justificativa:")
        print(match.justification)

        print("Evidências:")

        if not match.evidences:
            print("  nenhuma")
            continue

        for evidence in match.evidences:
            print(
                f"  - [{evidence.source.value}] "
                f"{evidence.text}"
            )


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
        job_document
    )

    print("\n2. Analisando currículo...")
    resume_profile = AIResumeAnalyzer().analyze(
        resume_document
    )

    matcher = AIRequirementMatcher()

    print("\n3. Avaliando hard skills...")
    hard_skill_matches = matcher.match(
        requirements=job_profile.hard_skills,
        resume=resume_profile,
    )

    print("\n4. Avaliando tecnologias...")
    technology_matches = matcher.match(
        requirements=job_profile.technologies,
        resume=resume_profile,
    )

    print("\n5. Avaliando soft skills...")
    soft_skill_matches = matcher.match(
        requirements=job_profile.soft_skills,
        resume=resume_profile,
    )

    print_matches(
        "HARD SKILLS",
        hard_skill_matches,
    )

    print_matches(
        "TECHNOLOGIES",
        technology_matches,
    )

    print_matches(
        "SOFT SKILLS",
        soft_skill_matches,
    )


if __name__ == "__main__":
    main()