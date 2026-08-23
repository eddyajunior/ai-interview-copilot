from app.schemas.document import ParsedDocument
from app.schemas.job_profile import (
    JobProfile,
    JobRequirement,
    RequirementImportance,
    SeniorityLevel,
)


class JobAnalyzer:
    TECHNOLOGIES = [
        "Java",
        "Python",
        "C#",
        ".NET",
        "JavaScript",
        "TypeScript",
        "React",
        "Angular",
        "Next.js",
        "AWS",
        "Azure",
        "GCP",
        "Kafka",
        "Kubernetes",
        "Docker",
        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Redis",
    ]

    SOFT_SKILLS = {
        "liderança técnica": "Liderança técnica",
        "comunicação": "Comunicação",
        "trabalho em equipe": "Trabalho em equipe",
        "resolução de problemas": "Resolução de problemas",
        "autonomia": "Autonomia",
    }

    def analyze(
        self,
        document: ParsedDocument,
    ) -> JobProfile:
        if not document.content.strip():
            raise ValueError(
                "O conteúdo da vaga não pode estar vazio."
            )

        content = document.content
        content_lower = content.lower()

        return JobProfile(
            title=self._identify_title(content),
            seniority=self._identify_seniority(
                content_lower
            ),
            summary=content,
            hard_skills=[],
            soft_skills=self._identify_soft_skills(
                content_lower
            ),
            technologies=self._identify_technologies(
                content_lower
            ),
            responsibilities=[],
            differentiators=[],
        )

    def _identify_title(
        self,
        content: str,
    ) -> str:
        first_line = content.splitlines()[0].strip()

        if first_line:
            return first_line

        return "Não identificado"

    def _identify_seniority(
        self,
        content: str,
    ) -> SeniorityLevel | None:
        seniority_terms = {
            SeniorityLevel.JUNIOR: [
                "junior",
                "júnior",
                "jr",
            ],
            SeniorityLevel.MID: [
                "pleno",
                "mid-level",
                "mid level",
            ],
            SeniorityLevel.SENIOR: [
                "senior",
                "sênior",
                "sr",
            ],
            SeniorityLevel.SPECIALIST: [
                "especialista",
                "specialist",
            ],
            SeniorityLevel.LEAD: [
                "tech lead",
                "technical lead",
            ],
        }

        for seniority, terms in seniority_terms.items():
            if any(
                term in content
                for term in terms
            ):
                return seniority

        return None

    def _identify_technologies(
        self,
        content: str,
    ) -> list[JobRequirement]:
        requirements = []

        for technology in self.TECHNOLOGIES:
            if technology.lower() in content:
                requirements.append(
                    JobRequirement(
                        name=technology,
                        importance=(
                            RequirementImportance.REQUIRED
                        ),
                        description=None,
                    )
                )

        return requirements

    def _identify_soft_skills(
        self,
        content: str,
    ) -> list[JobRequirement]:
        requirements = []

        for term, skill_name in self.SOFT_SKILLS.items():
            if term not in content:
                continue

            importance = (
                RequirementImportance.DESIRED
                if "diferencial" in content
                else RequirementImportance.REQUIRED
            )

            requirements.append(
                JobRequirement(
                    name=skill_name,
                    importance=importance,
                    description=None,
                )
            )

        return requirements