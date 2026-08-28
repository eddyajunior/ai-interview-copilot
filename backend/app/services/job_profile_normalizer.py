from app.schemas.job_profile import (
    JobProfile,
    JobRequirement,
    RequirementImportance,
)


IMPORTANCE_PRIORITY = {
    RequirementImportance.REQUIRED: 3,
    RequirementImportance.DESIRED: 2,
    RequirementImportance.OPTIONAL: 1,
}


class JobProfileNormalizer:
    def normalize(
        self,
        job: JobProfile,
    ) -> JobProfile:
        hard_skills = self._deduplicate_group(
            job.hard_skills
        )
        technologies = self._deduplicate_group(
            job.technologies
        )
        soft_skills = self._deduplicate_group(
            job.soft_skills
        )

        # HARD_SKILLS funciona como categoria mais genérica.
        # Se o mesmo requisito já foi classificado como
        # technology ou soft skill, removemos a duplicidade
        # de hard_skills.
        technology_names = {
            self._normalize_name(item.name)
            for item in technologies
        }

        soft_skill_names = {
            self._normalize_name(item.name)
            for item in soft_skills
        }

        hard_skills = [
            item
            for item in hard_skills
            if (
                self._normalize_name(item.name)
                not in technology_names
                and self._normalize_name(item.name)
                not in soft_skill_names
            )
        ]

        return JobProfile(
            title=job.title,
            seniority=job.seniority,
            summary=job.summary,
            hard_skills=hard_skills,
            soft_skills=soft_skills,
            technologies=technologies,
            responsibilities=list(
                dict.fromkeys(
                    job.responsibilities
                )
            ),
            differentiators=list(
                dict.fromkeys(
                    job.differentiators
                )
            ),
        )

    def _deduplicate_group(
        self,
        requirements: list[JobRequirement],
    ) -> list[JobRequirement]:
        selected: dict[
            str,
            JobRequirement,
        ] = {}

        order: list[str] = []

        for requirement in requirements:
            normalized_name = (
                self._normalize_name(
                    requirement.name
                )
            )

            if normalized_name not in selected:
                selected[
                    normalized_name
                ] = requirement
                order.append(normalized_name)
                continue

            current = selected[
                normalized_name
            ]

            selected[
                normalized_name
            ] = self._choose_requirement(
                current=current,
                candidate=requirement,
            )

        return [
            selected[name]
            for name in order
        ]

    @staticmethod
    def _choose_requirement(
        current: JobRequirement,
        candidate: JobRequirement,
    ) -> JobRequirement:
        current_priority = (
            IMPORTANCE_PRIORITY[
                current.importance
            ]
        )

        candidate_priority = (
            IMPORTANCE_PRIORITY[
                candidate.importance
            ]
        )

        if (
            candidate_priority
            > current_priority
        ):
            return candidate

        if (
            candidate_priority
            < current_priority
        ):
            return current

        current_description_length = len(
            current.description or ""
        )

        candidate_description_length = len(
            candidate.description or ""
        )

        if (
            candidate_description_length
            > current_description_length
        ):
            return candidate

        return current

    @staticmethod
    def _normalize_name(
        value: str,
    ) -> str:
        return " ".join(
            value.strip().casefold().split()
        )