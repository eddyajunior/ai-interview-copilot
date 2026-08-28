from dataclasses import dataclass

from app.schemas.evidence import (
    Evidence,
    EvidenceSource,
)
from app.schemas.job_profile import (
    JobProfile,
    JobRequirement,
    RequirementImportance,
)
from app.schemas.resume_profile import (
    ResumeProfile,
    ResumeSkillEvidence,
)
from app.schemas.scoring import (
    AssessmentStatus,
    EvidenceStrength,
    SCORING_RULES,
    SkillScore,
)
from app.schemas.candidate_assessment import (
    CandidateAssessment,
    ConfidenceLevel,
    Recommendation,
    SkillAssessment,
    SkillType,
)
from app.schemas.requirement_match import (
    MatchType,
    RequirementMatch,
    RequirementMatchSet,
)
from app.services.ai_requirement_matcher import (
    AIRequirementMatcher,
)


@dataclass
class SkillScoreResult:
    name: str
    score: SkillScore
    evidence_strength: EvidenceStrength
    status: AssessmentStatus
    evidences: list[Evidence]
    justification: str


@dataclass
class AdherenceResult:
    percentage: float
    weighted_score: float
    maximum_weighted_score: float
    evaluated_requirements: int


IMPORTANCE_WEIGHTS = {
    RequirementImportance.REQUIRED: 3,
    RequirementImportance.DESIRED: 2,
    RequirementImportance.OPTIONAL: 1,
}

SCORE_PERCENTAGES = {
    SkillScore.NOT_EVIDENCED: 0.00,
    SkillScore.LIMITED: 0.25,
    SkillScore.COMPATIBLE: 0.50,
    SkillScore.STRONG: 0.75,
    SkillScore.VERY_STRONG: 1.00,
}


class CandidateScorer:
    TECHNOLOGY_ALIASES = {
        "aws": {
            "aws",
            "amazon aws",
            "amazon web services",
        },
        "postgresql": {
            "postgresql",
            "postgres",
            "postgres sql",
        },
        ".net": {
            ".net",
            ".net core",
            "dotnet",
            "dotnet core",
        },
        "javascript": {
            "javascript",
            "java script",
            "js",
        },
        "typescript": {
            "typescript",
            "type script",
            "ts",
        },
        "kubernetes": {
            "kubernetes",
            "k8s",
        },
    }

    def score_technologies(
        self,
        job: JobProfile,
        resume: ResumeProfile,
    ) -> list[SkillScoreResult]:
        return self._score_requirements(
            requirements=job.technologies,
            resume_skills=resume.technologies,
            resume=resume,
            use_technology_aliases=True,
        )

    def score_hard_skills(
        self,
        job: JobProfile,
        resume: ResumeProfile,
    ) -> list[SkillScoreResult]:
        return self._score_requirements(
            requirements=job.hard_skills,
            resume_skills=resume.hard_skills,
            resume=resume,
            use_technology_aliases=False,
        )

    def score_soft_skills(
        self,
        job: JobProfile,
        resume: ResumeProfile,
    ) -> list[SkillScoreResult]:
        results: list[SkillScoreResult] = []

        resume_index = {
            self._normalize(item.skill): item
            for item in resume.soft_skill_evidences
        }

        for requirement in job.soft_skills:
            requirement_key = self._normalize(
                requirement.name
            )

            resume_skill = resume_index.get(
                requirement_key
            )

            if resume_skill is None:
                results.append(
                    self._build_not_evidenced_soft_skill_score(
                        requirement.name
                    )
                )
                continue

            results.append(
                self._build_soft_skill_score(
                    requirement.name,
                    resume_skill,
                )
            )

        return results

    def calculate_adherence(
        self,
        job: JobProfile,
        resume: ResumeProfile,
    ) -> AdherenceResult:
        technology_scores = self.score_technologies(
            job,
            resume,
        )

        hard_skill_scores = self.score_hard_skills(
            job,
            resume,
        )

        soft_skill_scores = self.score_soft_skills(
            job,
            resume,
        )

        weighted_score = 0.0
        maximum_weighted_score = 0.0

        weighted_score += self._calculate_group_weight(
            requirements=job.technologies,
            scores=technology_scores,
        )

        weighted_score += self._calculate_group_weight(
            requirements=job.hard_skills,
            scores=hard_skill_scores,
        )

        weighted_score += self._calculate_group_weight(
            requirements=job.soft_skills,
            scores=soft_skill_scores,
        )

        maximum_weighted_score += (
            self._calculate_maximum_group_weight(
                job.technologies
            )
        )

        maximum_weighted_score += (
            self._calculate_maximum_group_weight(
                job.hard_skills
            )
        )

        maximum_weighted_score += (
            self._calculate_maximum_group_weight(
                job.soft_skills
            )
        )

        evaluated_requirements = (
            len(job.technologies)
            + len(job.hard_skills)
            + len(job.soft_skills)
        )

        if maximum_weighted_score == 0:
            return AdherenceResult(
                percentage=0.0,
                weighted_score=0.0,
                maximum_weighted_score=0.0,
                evaluated_requirements=0,
            )

        percentage = (
            weighted_score
            / maximum_weighted_score
        ) * 100

        return AdherenceResult(
            percentage=round(
                percentage,
                2,
            ),
            weighted_score=round(
                weighted_score,
                2,
            ),
            maximum_weighted_score=round(
                maximum_weighted_score,
                2,
            ),
            evaluated_requirements=(
                evaluated_requirements
            ),
        )

    def build_candidate_assessment(
        self,
        job: JobProfile,
        resume: ResumeProfile,
    ) -> CandidateAssessment:
        matcher = AIRequirementMatcher()

        technology_matches = matcher.match(
            requirements=job.technologies,
            resume=resume,
        )

        hard_skill_matches = matcher.match(
            requirements=job.hard_skills,
            resume=resume,
        )

        soft_skill_matches = matcher.match(
            requirements=job.soft_skills,
            resume=resume,
        )

        technology_scores = (
            self.score_requirement_matches(
                technology_matches
            )
        )

        hard_skill_scores = (
            self.score_requirement_matches(
                hard_skill_matches
            )
        )

        soft_skill_scores = (
            self.score_requirement_matches(
                soft_skill_matches
            )
        )

        adherence = (
            self.calculate_adherence_from_scores(
                job=job,
                technology_scores=technology_scores,
                hard_skill_scores=hard_skill_scores,
                soft_skill_scores=soft_skill_scores,
            )
        )

        technologies = [
            self._to_skill_assessment(
                result,
                SkillType.TECHNOLOGY,
            )
            for result in technology_scores
        ]

        hard_skills = [
            self._to_skill_assessment(
                result,
                SkillType.HARD_SKILL,
            )
            for result in hard_skill_scores
        ]

        soft_skills = [
            self._to_skill_assessment(
                result,
                SkillType.SOFT_SKILL,
            )
            for result in soft_skill_scores
        ]

        all_scores = (
            technology_scores
            + hard_skill_scores
            + soft_skill_scores
        )

        strengths = self._build_strengths(
            all_scores
        )

        weaknesses = self._build_evidence_gaps(
            all_scores
        )

        summary = (
            f"Aderência documental ponderada de "
            f"{adherence.percentage:.2f}% considerando "
            f"{adherence.evaluated_requirements} requisitos "
            f"avaliados. O percentual representa apenas "
            f"evidências encontradas no currículo em relação "
            f"à vaga e não constitui recomendação automática "
            f"de contratação."
        )

        recommendation = self._build_recommendation(
            job=job,
            technology_scores=technology_scores,
            hard_skill_scores=hard_skill_scores,
            soft_skill_scores=soft_skill_scores,
        )

        return CandidateAssessment(
            candidate_name=resume.candidate_name,
            job_title=job.title,
            summary=summary,
            adherence_percentage=(
                adherence.percentage
            ),
            strengths=strengths,
            weaknesses=weaknesses,
            hard_skills=hard_skills,
            soft_skills=soft_skills,
            technologies=technologies,
            questions=[],
            risks=[],
            interviewer_comments=[],
            recommendation=recommendation,
        )

    def _score_requirements(
        self,
        requirements,
        resume_skills: list[ResumeSkillEvidence],
        resume: ResumeProfile,
        use_technology_aliases: bool,
    ) -> list[SkillScoreResult]:
        results: list[SkillScoreResult] = []

        resume_index = {
            self._prepare_key(
                item.skill,
                use_technology_aliases,
            ): item
            for item in resume_skills
        }

        for requirement in requirements:
            requirement_key = self._prepare_key(
                requirement.name,
                use_technology_aliases,
            )

            resume_skill = resume_index.get(
                requirement_key
            )

            if resume_skill is None:
                results.append(
                    self._build_not_evidenced_score(
                        requirement.name
                    )
                )
                continue

            results.append(
                self._build_evidenced_score(
                    requirement.name,
                    resume_skill,
                    resume,
                    use_technology_aliases,
                )
            )

        return results

    def _build_evidenced_score(
        self,
        skill_name: str,
        resume_skill: ResumeSkillEvidence,
        resume: ResumeProfile,
        use_technology_aliases: bool,
    ) -> SkillScoreResult:
        evidences = self._deduplicate_evidences(
            resume_skill.evidence
        )

        source_count = len(
            {
                evidence.source
                for evidence in evidences
            }
        )

        has_experience_evidence = any(
            evidence.source
            == EvidenceSource.EXPERIENCE
            for evidence in evidences
        )

        has_measurable_result = (
            self._has_related_measurable_result(
                skill_name,
                resume,
                use_technology_aliases,
            )
        )

        if (
            len(evidences) >= 2
            and source_count >= 2
            and has_experience_evidence
            and has_measurable_result
        ):
            return SkillScoreResult(
                name=skill_name,
                score=SkillScore.VERY_STRONG,
                evidence_strength=(
                    EvidenceStrength.HIGH
                ),
                status=AssessmentStatus.STRONG,
                evidences=evidences,
                justification=(
                    "A competência possui múltiplas evidências "
                    "provenientes de fontes diferentes, incluindo "
                    "experiência profissional e resultado mensurável."
                ),
            )

        if (
            len(evidences) >= 2
            and has_experience_evidence
        ):
            return SkillScoreResult(
                name=skill_name,
                score=SkillScore.STRONG,
                evidence_strength=(
                    EvidenceStrength.HIGH
                ),
                status=AssessmentStatus.STRONG,
                evidences=evidences,
                justification=(
                    "A competência possui múltiplas evidências "
                    "relevantes no currículo, incluindo "
                    "experiência profissional."
                ),
            )

        if has_experience_evidence:
            return SkillScoreResult(
                name=skill_name,
                score=SkillScore.COMPATIBLE,
                evidence_strength=(
                    EvidenceStrength.MEDIUM
                ),
                status=AssessmentStatus.COMPATIBLE,
                evidences=evidences,
                justification=(
                    "A competência possui evidência explícita "
                    "em experiência profissional."
                ),
            )

        return SkillScoreResult(
            name=skill_name,
            score=SkillScore.LIMITED,
            evidence_strength=(
                EvidenceStrength.LOW
            ),
            status=AssessmentStatus.NEEDS_VALIDATION,
            evidences=evidences,
            justification=(
                "A competência foi encontrada no currículo, "
                "mas sem evidência direta em experiência "
                "profissional. O conhecimento deve ser "
                "validado na entrevista."
            ),
        )

    def _build_soft_skill_score(
        self,
        skill_name: str,
        resume_skill: ResumeSkillEvidence,
    ) -> SkillScoreResult:
        evidences = self._deduplicate_evidences(
            resume_skill.evidence
        )

        experience_evidences = [
            evidence
            for evidence in evidences
            if evidence.source
            == EvidenceSource.EXPERIENCE
        ]

        experience_references = {
            evidence.source_reference
            for evidence in experience_evidences
            if evidence.source_reference
        }

        if (
            len(experience_evidences) >= 2
            and len(experience_references) >= 2
        ):
            return SkillScoreResult(
                name=skill_name,
                score=SkillScore.STRONG,
                evidence_strength=(
                    EvidenceStrength.HIGH
                ),
                status=AssessmentStatus.STRONG,
                evidences=evidences,
                justification=(
                    "A competência comportamental possui "
                    "múltiplas evidências explícitas em "
                    "contextos profissionais diferentes. "
                    "Ainda assim, deve ser validada "
                    "durante a entrevista."
                ),
            )

        if experience_evidences:
            return SkillScoreResult(
                name=skill_name,
                score=SkillScore.COMPATIBLE,
                evidence_strength=(
                    EvidenceStrength.MEDIUM
                ),
                status=AssessmentStatus.COMPATIBLE,
                evidences=evidences,
                justification=(
                    "Existe evidência explícita da competência "
                    "comportamental em contexto profissional. "
                    "A entrevista deve validar sua consistência."
                ),
            )

        return SkillScoreResult(
            name=skill_name,
            score=SkillScore.LIMITED,
            evidence_strength=(
                EvidenceStrength.LOW
            ),
            status=AssessmentStatus.NEEDS_VALIDATION,
            evidences=evidences,
            justification=(
                "A competência comportamental foi identificada "
                "no currículo, mas sem evidência contextual "
                "suficiente em experiência profissional. "
                "Deve ser aprofundada durante a entrevista."
            ),
        )

    @staticmethod
    def _build_not_evidenced_soft_skill_score(
        skill_name: str,
    ) -> SkillScoreResult:
        return SkillScoreResult(
            name=skill_name,
            score=SkillScore.NOT_EVIDENCED,
            evidence_strength=(
                EvidenceStrength.NONE
            ),
            status=(
                AssessmentStatus.NOT_EVIDENCED
            ),
            evidences=[],
            justification=(
                "Não foram encontradas evidências explícitas "
                "desta competência comportamental no currículo. "
                "Isso não significa ausência da competência e "
                "ela deve ser investigada durante a entrevista."
            ),
        )

    @staticmethod
    def _build_not_evidenced_score(
        skill_name: str,
    ) -> SkillScoreResult:
        return SkillScoreResult(
            name=skill_name,
            score=SkillScore.NOT_EVIDENCED,
            evidence_strength=(
                EvidenceStrength.NONE
            ),
            status=(
                AssessmentStatus.NOT_EVIDENCED
            ),
            evidences=[],
            justification=(
                "Não foram encontradas evidências explícitas "
                "desta competência no currículo. "
                "Isso não significa ausência de conhecimento "
                "e deve ser validado durante a entrevista."
            ),
        )

    def _has_related_measurable_result(
        self,
        skill_name: str,
        resume: ResumeProfile,
        use_technology_aliases: bool,
    ) -> bool:
        if use_technology_aliases:
            canonical_name = self._canonicalize(
                skill_name
            )

            aliases = self.TECHNOLOGY_ALIASES.get(
                canonical_name,
                {canonical_name},
            )

            terms = {
                self._normalize(alias)
                for alias in aliases
            }

        else:
            terms = {
                self._normalize(skill_name)
            }

        for result in resume.measurable_results:
            normalized_result = self._normalize(
                result
            )

            if any(
                term in normalized_result
                for term in terms
            ):
                return True

        return False

    def _prepare_key(
        self,
        value: str,
        use_technology_aliases: bool,
    ) -> str:
        if use_technology_aliases:
            return self._canonicalize(value)

        return self._normalize(value)

    @staticmethod
    def _deduplicate_evidences(
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
                evidence.source_reference,
                evidence.page,
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(evidence)

        return unique

    @classmethod
    def _canonicalize(
        cls,
        value: str,
    ) -> str:
        normalized = cls._normalize(value)

        for (
            canonical,
            aliases,
        ) in cls.TECHNOLOGY_ALIASES.items():
            normalized_aliases = {
                cls._normalize(alias)
                for alias in aliases
            }

            if normalized in normalized_aliases:
                return canonical

        return normalized

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:
        return " ".join(
            value.strip().casefold().split()
        )

    def _calculate_group_weight(
        self,
        requirements,
        scores: list[SkillScoreResult],
    ) -> float:
        score_index = {
            self._normalize(score.name): score
            for score in scores
        }

        total = 0.0

        for requirement in requirements:
            score = score_index[
                self._normalize(
                    requirement.name
                )
            ]

            importance_weight = (
                IMPORTANCE_WEIGHTS[
                    requirement.importance
                ]
            )

            score_percentage = (
                SCORE_PERCENTAGES[
                    score.score
                ]
            )

            total += (
                importance_weight
                * score_percentage
            )

        return total

    @staticmethod
    def _calculate_maximum_group_weight(
        requirements,
    ) -> float:
        return sum(
            IMPORTANCE_WEIGHTS[
                requirement.importance
            ]
            for requirement in requirements
        )

    def _to_skill_assessment(
        self,
        result: SkillScoreResult,
        skill_type: SkillType,
    ) -> SkillAssessment:
        confidence = self._calculate_confidence(
            result=result,
            skill_type=skill_type,
        )

        return SkillAssessment(
            name=result.name,
            type=skill_type,
            score=result.score.value,
            evidence=result.evidences,
            justification=result.justification,
            confidence=confidence,
            status=result.status.value,
        )

    @staticmethod
    def _calculate_confidence(
        result: SkillScoreResult,
        skill_type: SkillType,
    ) -> ConfidenceLevel:
        if result.evidence_strength in {
            EvidenceStrength.NONE,
            EvidenceStrength.LOW,
        }:
            return ConfidenceLevel.LOW

        if (
            result.evidence_strength
            == EvidenceStrength.MEDIUM
        ):
            return ConfidenceLevel.MEDIUM

        if skill_type == SkillType.SOFT_SKILL:
            return ConfidenceLevel.MEDIUM

        return ConfidenceLevel.HIGH

    @staticmethod
    def _build_strengths(
        scores: list[SkillScoreResult],
    ) -> list[str]:
        return [
            (
                f"{score.name}: evidências consistentes "
                f"encontradas no currículo."
            )
            for score in scores
            if score.score in {
                SkillScore.STRONG,
                SkillScore.VERY_STRONG,
            }
        ]

    @staticmethod
    def _build_evidence_gaps(
        scores: list[SkillScoreResult],
    ) -> list[str]:
        return [
            (
                f"{score.name}: evidência insuficiente "
                f"no currículo; validar durante a entrevista."
            )
            for score in scores
            if score.score in {
                SkillScore.NOT_EVIDENCED,
                SkillScore.LIMITED,
            }
        ]

    def _build_recommendation(
        self,
        job: JobProfile,
        technology_scores: list[SkillScoreResult],
        hard_skill_scores: list[SkillScoreResult],
        soft_skill_scores: list[SkillScoreResult],
    ) -> Recommendation:
        required_gaps = 0

        groups = [
            (
                job.technologies,
                technology_scores,
            ),
            (
                job.hard_skills,
                hard_skill_scores,
            ),
            (
                job.soft_skills,
                soft_skill_scores,
            ),
        ]

        for requirements, scores in groups:
            score_index = {
                self._normalize(
                    score.name
                ): score
                for score in scores
            }

            for requirement in requirements:
                if (
                    requirement.importance
                    != RequirementImportance.REQUIRED
                ):
                    continue

                score = score_index[
                    self._normalize(
                        requirement.name
                    )
                ]

                if score.score in {
                    SkillScore.NOT_EVIDENCED,
                    SkillScore.LIMITED,
                }:
                    required_gaps += 1

        if required_gaps:
            short_term = (
                f"Validar durante a entrevista "
                f"{required_gaps} requisito(s) obrigatório(s) "
                f"com evidência ausente ou limitada "
                f"no currículo."
            )
        else:
            short_term = (
                "Aprofundar durante a entrevista as "
                "evidências dos principais requisitos "
                "obrigatórios da vaga."
            )

        return Recommendation(
            short_term=short_term,
            medium_term=(
                "Consolidar a avaliação após a entrevista, "
                "incorporando as evidências obtidas nas "
                "respostas do candidato."
            ),
            long_term=(
                "Utilizar a avaliação consolidada para "
                "apoiar a decisão humana do processo "
                "seletivo, sem tratar o percentual "
                "documental como decisão automática."
            ),
        )

    def score_requirement_match(
        self,
        match: RequirementMatch,
    ) -> SkillScoreResult:
        evidences = self._deduplicate_evidences(
            match.evidences
        )

        if (
            match.match_type == MatchType.NONE
            or not evidences
        ):
            rule = SCORING_RULES[
                SkillScore.NOT_EVIDENCED
            ]

            return SkillScoreResult(
                name=match.requirement_name,
                score=rule.score,
                evidence_strength=(
                    rule.evidence_strength
                ),
                status=rule.status,
                evidences=[],
                justification=(
                    "Não foram encontradas evidências "
                    "documentais suficientes para este "
                    "requisito. Isso não significa ausência "
                    "da competência e deve ser validado "
                    "durante a entrevista."
                ),
            )

        experience_evidences = [
            evidence
            for evidence in evidences
            if (
                evidence.source
                == EvidenceSource.EXPERIENCE
            )
        ]

        education_evidences = [
            evidence
            for evidence in evidences
            if evidence.source
            == EvidenceSource.EDUCATION
        ]

        certification_evidences = [
            evidence
            for evidence in evidences
            if evidence.source
            == EvidenceSource.CERTIFICATION
        ]

        source_types = {
            evidence.source
            for evidence in evidences
        }

        source_references = {
            evidence.source_reference
            for evidence in experience_evidences
            if evidence.source_reference
        }

        if match.match_type == MatchType.PARTIAL:
            score = (
                SkillScore.LIMITED
                if not experience_evidences
                else SkillScore.COMPATIBLE
            )

        elif (
            len(evidences) >= 2
            and experience_evidences
            and len(source_types) >= 2
        ):
            score = SkillScore.STRONG

        elif (
            len(evidences) >= 2
            and len(source_references) >= 2
        ):
            score = SkillScore.STRONG

        elif experience_evidences:
            score = SkillScore.COMPATIBLE

        elif education_evidences:
            score = SkillScore.COMPATIBLE

        elif certification_evidences:
            score = SkillScore.COMPATIBLE

        else:
            score = SkillScore.LIMITED

        rule = SCORING_RULES[
            score
        ]

        return SkillScoreResult(
            name=match.requirement_name,
            score=rule.score,
            evidence_strength=(
                rule.evidence_strength
            ),
            status=rule.status,
            evidences=evidences,
            justification=(
                f"{match.justification} "
                f"{rule.description}"
            ),
        )

    def score_requirement_matches(
        self,
        match_set: RequirementMatchSet,
    ) -> list[SkillScoreResult]:
        return [
            self.score_requirement_match(
                match
            )
            for match in match_set.matches
        ]

    def calculate_adherence_from_scores(
        self,
        job: JobProfile,
        technology_scores: list[SkillScoreResult],
        hard_skill_scores: list[SkillScoreResult],
        soft_skill_scores: list[SkillScoreResult],
    ) -> AdherenceResult:
        score_by_name = {
            self._normalize(
                result.name
            ): result
            for result in (
                technology_scores
                + hard_skill_scores
                + soft_skill_scores
            )
        }

        requirements = (
            job.technologies
            + job.hard_skills
            + job.soft_skills
        )

        weighted_score = 0.0
        maximum_weighted_score = 0.0

        for requirement in requirements:
            weight = IMPORTANCE_WEIGHTS[
                requirement.importance
            ]

            maximum_weighted_score += weight

            result = score_by_name.get(
                self._normalize(
                    requirement.name
                )
            )

            if result is None:
                continue

            percentage = SCORE_PERCENTAGES[
                result.score
            ]

            weighted_score += (
                percentage
                * weight
            )

        if maximum_weighted_score == 0:
            percentage = 0.0
        else:
            percentage = (
                weighted_score
                / maximum_weighted_score
                * 100
            )

        return AdherenceResult(
            percentage=round(
                percentage,
                2,
            ),
            weighted_score=round(
                weighted_score,
                2,
            ),
            maximum_weighted_score=round(
                maximum_weighted_score,
                2,
            ),
            evaluated_requirements=len(
                requirements
            ),
        )