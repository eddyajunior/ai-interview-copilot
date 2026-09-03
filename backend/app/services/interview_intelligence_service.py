from app.schemas.candidate_assessment import (
    CandidateAssessment,
)
from app.services.ai_interview_question_generator import (
    AIInterviewQuestionGenerator,
)
from app.services.interview_focus_builder import (
    InterviewFocusBuilder,
)
from app.services.interview_focus_selector import (
    InterviewFocusSelector,
)


class InterviewIntelligenceService:
    def __init__(
        self,
        focus_builder: InterviewFocusBuilder | None = None,
        focus_selector: InterviewFocusSelector | None = None,
        question_generator: (
            AIInterviewQuestionGenerator | None
        ) = None,
    ):
        self.focus_builder = (
            focus_builder
            or InterviewFocusBuilder()
        )

        self.focus_selector = (
            focus_selector
            or InterviewFocusSelector()
        )

        self.question_generator = (
            question_generator
            or AIInterviewQuestionGenerator()
        )

    def enrich(
        self,
        assessment: CandidateAssessment,
    ) -> CandidateAssessment:
        focuses = self.focus_builder.build(
            assessment
        )

        selected_focuses = (
            self.focus_selector.select(
                focuses
            )
        )

        question_set = (
            self.question_generator.generate(
                selected_focuses
            )
        )

        return assessment.model_copy(
            update={
                "questions": (
                    question_set.questions
                )
            }
        )