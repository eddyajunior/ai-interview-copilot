from app.schemas.evidence import (
    Evidence,
    EvidenceSource,
)
from app.schemas.evidence_catalog import EvidenceCatalog
from app.schemas.resume_profile import ResumeProfile


class ResumeEvidenceCatalog:
    def build(
        self,
        resume: ResumeProfile,
    ) -> EvidenceCatalog:
        evidences: list[Evidence] = []

        self._add_skill_evidences(
            evidences,
            resume,
        )

        self._add_professional_summary(
            evidences,
            resume,
        )

        self._add_experiences(
            evidences,
            resume,
        )

        self._add_education(
            evidences,
            resume,
        )

        self._add_certifications(
            evidences,
            resume,
        )

        return EvidenceCatalog(
            evidences=self._deduplicate(
                evidences
            )
        )

    @staticmethod
    def _add_skill_evidences(
        evidences: list[Evidence],
        resume: ResumeProfile,
    ) -> None:
        groups = (
            resume.hard_skills
            + resume.soft_skill_evidences
            + resume.technologies
        )

        for skill in groups:
            evidences.extend(
                skill.evidence
            )

    @staticmethod
    def _add_professional_summary(
        evidences: list[Evidence],
        resume: ResumeProfile,
    ) -> None:
        if not resume.professional_summary:
            return

        evidences.append(
            Evidence(
                text=resume.professional_summary,
                source=(
                    EvidenceSource.PROFESSIONAL_SUMMARY
                ),
                source_reference=(
                    "Resumo profissional"
                ),
                page=None,
            )
        )

    @staticmethod
    def _add_experiences(
        evidences: list[Evidence],
        resume: ResumeProfile,
    ) -> None:
        for experience in resume.experiences:
            reference = (
                f"{experience.role}"
            )

            if experience.company:
                reference += (
                    f" - {experience.company}"
                )

            texts = (
                experience.responsibilities
                + experience.achievements
            )

            for text in texts:
                evidences.append(
                    Evidence(
                        text=text,
                        source=EvidenceSource.EXPERIENCE,
                        source_reference=reference,
                        page=None,
                    )
                )

    @staticmethod
    def _add_education(
        evidences: list[Evidence],
        resume: ResumeProfile,
    ) -> None:
        for education in resume.education:
            parts = [
                education.institution,
                education.course,
                education.level,
                education.completion_date,
            ]

            text = " — ".join(
                part
                for part in parts
                if part
            )

            if not text:
                continue

            evidences.append(
                Evidence(
                    text=text,
                    source=EvidenceSource.EDUCATION,
                    source_reference=(
                        education.institution
                    ),
                    page=None,
                )
            )

    @staticmethod
    def _add_certifications(
        evidences: list[Evidence],
        resume: ResumeProfile,
    ) -> None:
        for certification in resume.certifications:
            parts = [
                certification.name,
                certification.issuer,
                certification.date,
            ]

            text = " — ".join(
                part
                for part in parts
                if part
            )

            evidences.append(
                Evidence(
                    text=text,
                    source=(
                        EvidenceSource.CERTIFICATION
                    ),
                    source_reference=(
                        certification.issuer
                    ),
                    page=None,
                )
            )

    @staticmethod
    def _deduplicate(
        evidences: list[Evidence],
    ) -> list[Evidence]:
        unique: list[Evidence] = []
        seen: set[tuple] = set()

        for evidence in evidences:
            key = (
                " ".join(
                    evidence.text
                    .strip()
                    .casefold()
                    .split()
                ),
                evidence.source,
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(
                evidence
            )

        return unique