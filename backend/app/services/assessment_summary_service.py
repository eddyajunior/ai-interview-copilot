from app.schemas.candidate_assessment import (
    CandidateAssessment,
    Recommendation,
)
from app.services.ai_assessment_summary_generator import (
    AIAssessmentSummaryGenerator,
)


class AssessmentSummaryService:
    def __init__(
        self,
        summary_generator: AIAssessmentSummaryGenerator | None = None,
    ):
        self.summary_generator = (
            summary_generator
            or AIAssessmentSummaryGenerator()
        )

    def enrich(
        self,
        assessment: CandidateAssessment,
    ) -> CandidateAssessment:
        summary = self.summary_generator.generate(
            assessment
        )

        recommendation = Recommendation(
            short_term=(
                summary.recommendation.short_term
            ),
            medium_term=(
                summary.recommendation.medium_term
            ),
            long_term=(
                summary.recommendation.long_term
            ),
        )

        return assessment.model_copy(
            update={
                "interviewer_comments": (
                    summary.interviewer_comments
                ),
                "recommendation": recommendation,
            }
        )