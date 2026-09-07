from app.schemas.candidate_assessment import (
    CandidateAssessment,
)
from app.schemas.interview_session import (
    InterviewQuestionRecord,
    InterviewSession,
)


class InterviewSessionFactory:
    def create(
        self,
        assessment: CandidateAssessment,
    ) -> InterviewSession:
        questions = [
            InterviewQuestionRecord(
                question_index=index,
                competency=question.competency,
                question=question.question,
            )
            for index, question in enumerate(
                assessment.questions
            )
        ]

        return InterviewSession(
            candidate_name=assessment.candidate_name,
            job_title=assessment.job_title,
            questions=questions,
        )