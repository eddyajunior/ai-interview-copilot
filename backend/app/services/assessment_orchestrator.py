from app.schemas.candidate_assessment import CandidateAssessment
from app.schemas.document import ParsedDocument
from app.services.ai_job_analyzer import AIJobAnalyzer
from app.services.ai_resume_analyzer import AIResumeAnalyzer
from app.services.assessment_summary_service import (
    AssessmentSummaryService,
)
from app.services.candidate_scorer import CandidateScorer
from app.services.interview_intelligence_service import (
    InterviewIntelligenceService,
)
from app.services.risk_intelligence_service import (
    RiskIntelligenceService,
)


class AssessmentOrchestrator:
    def __init__(
        self,
        job_analyzer: AIJobAnalyzer | None = None,
        resume_analyzer: AIResumeAnalyzer | None = None,
        candidate_scorer: CandidateScorer | None = None,
        interview_service: InterviewIntelligenceService | None = None,
        risk_service: RiskIntelligenceService | None = None,
        summary_service: AssessmentSummaryService | None = None,
    ):
        self.job_analyzer = job_analyzer or AIJobAnalyzer()
        self.resume_analyzer = (
            resume_analyzer or AIResumeAnalyzer()
        )
        self.candidate_scorer = (
            candidate_scorer or CandidateScorer()
        )
        self.interview_service = (
            interview_service
            or InterviewIntelligenceService()
        )
        self.risk_service = (
            risk_service
            or RiskIntelligenceService()
        )
        self.summary_service = (
            summary_service
            or AssessmentSummaryService()
        )

    def execute(
        self,
        job_document: ParsedDocument,
        resume_document: ParsedDocument,
    ) -> CandidateAssessment:
        job_profile = self.job_analyzer.analyze(
            job_document
        )

        resume_profile = self.resume_analyzer.analyze(
            resume_document
        )

        assessment = (
            self.candidate_scorer
            .build_candidate_assessment(
                job_profile,
                resume_profile,
            )
        )

        assessment = self.interview_service.enrich(
            assessment
        )

        assessment = self.risk_service.enrich(
            assessment
        )

        assessment = self.summary_service.enrich(
            assessment
        )

        return assessment