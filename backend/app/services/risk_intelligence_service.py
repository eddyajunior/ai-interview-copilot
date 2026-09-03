from app.schemas.candidate_assessment import (
    CandidateAssessment,
)
from app.services.ai_risk_generator import (
    AIRiskGenerator,
)
from app.services.risk_focus_builder import (
    RiskFocusBuilder,
)
from app.services.risk_focus_selector import (
    RiskFocusSelector,
)


class RiskIntelligenceService:
    def __init__(
        self,
        focus_builder: RiskFocusBuilder | None = None,
        focus_selector: RiskFocusSelector | None = None,
        risk_generator: AIRiskGenerator | None = None,
    ):
        self.focus_builder = (
            focus_builder
            or RiskFocusBuilder()
        )

        self.focus_selector = (
            focus_selector
            or RiskFocusSelector()
        )

        self.risk_generator = (
            risk_generator
            or AIRiskGenerator()
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

        risks = self.risk_generator.generate(
            selected_focuses
        )

        return assessment.model_copy(
            update={
                "risks": risks,
            }
        )