from fastapi.testclient import TestClient

from app.main import app

from app.schemas.candidate_assessment import CandidateAssessment


client = TestClient(app)


def build_assessment_payload():
    return {
        "candidate_name": "Candidato Teste",
        "job_title": "Engineering Manager",
        "summary": "Resumo do assessment.",
        "adherence_percentage": 75.0,
        "strengths": [],
        "weaknesses": [],
        "hard_skills": [],
        "soft_skills": [],
        "technologies": [],
        "questions": [
            {
                "category": "hard_skill",
                "competency": "Arquitetura",
                "question": (
                    "Conte sobre uma decisão "
                    "arquitetural complexa."
                ),
                "reason": (
                    "Validar experiência arquitetural."
                ),
                "priority": "high",
                "follow_up": None,
                "what_to_observe": [
                    "Clareza dos trade-offs",
                ],
            },
            {
                "category": "soft_skill",
                "competency": "Liderança",
                "question": (
                    "Como você conduz conflitos "
                    "técnicos no time?"
                ),
                "reason": (
                    "Validar capacidade de liderança."
                ),
                "priority": "medium",
                "follow_up": None,
                "what_to_observe": [
                    "Capacidade de mediação",
                ],
            },
        ],
        "risks": [],
        "interviewer_comments": [],
        "recommendation": {
            "short_term": "Validar competências.",
            "medium_term": "Consolidar avaliação.",
            "long_term": "Acompanhar evolução.",
        },
    }


def test_creates_interview_session():
    response = client.post(
        "/api/v1/interview-sessions",
        json=build_assessment_payload(),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["session_id"]
    assert body["candidate_name"] == (
        "Candidato Teste"
    )

    assert body["job_title"] == (
        "Engineering Manager"
    )

    assert body["started_at"] is None
    assert body["completed_at"] is None

    assert len(body["questions"]) == 2
    assert body["final_notes"] is None


def test_session_questions_start_pending():
    response = client.post(
        "/api/v1/interview-sessions",
        json=build_assessment_payload(),
    )

    body = response.json()

    first_question = body["questions"][0]

    assert first_question["question_index"] == 0
    assert first_question["competency"] == (
        "Arquitetura"
    )

    assert first_question["status"] == "pending"

    assert (
        first_question["evaluation"]
        == "not_evaluated"
    )

    assert (
        first_question["evidence_strength"]
        == "not_evaluated"
    )

    assert (
        first_question["interviewer_notes"]
        is None
    )

    assert (
        first_question["response_summary"]
        is None
    )


def test_rejects_invalid_assessment():
    payload = build_assessment_payload()

    payload["job_title"] = ""

    response = client.post(
        "/api/v1/interview-sessions",
        json=payload,
    )

    assert response.status_code == 422


def test_creates_unique_session_ids():
    payload = build_assessment_payload()

    first_response = client.post(
        "/api/v1/interview-sessions",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/interview-sessions",
        json=payload,
    )

    first_session_id = (
        first_response.json()["session_id"]
    )

    second_session_id = (
        second_response.json()["session_id"]
    )

    assert first_session_id != second_session_id

def build_assessment() -> CandidateAssessment:
    return CandidateAssessment.model_validate(
        {
            "candidate_name": "Edson Amaral",
            "job_title": "Engineering Manager",
            "summary": "Assessment de teste.",
            "adherence_percentage": 80.0,
            "strengths": [],
            "weaknesses": [],
            "hard_skills": [],
            "soft_skills": [],
            "technologies": [],
            "questions": [],
            "risks": [],
            "interviewer_comments": [],
            "recommendation": {
                "short_term": "Validar competências na entrevista.",
                "medium_term": "Acompanhar evolução.",
                "long_term": "Avaliar aderência ao papel.",
            },
        }
    )

def test_patch_interview_session():
    assessment = build_assessment()

    create_response = client.post(
        "/api/v1/interview-sessions",
        json=assessment.model_dump(
            mode="json",
        ),
    )

    assert create_response.status_code == 201

    session = create_response.json()

    session["final_notes"] = (
        "Boa entrevista."
    )

    response = client.patch(
        (
            "/api/v1/interview-sessions/"
            f"{session['session_id']}"
        ),
        json=session,
    )

    assert response.status_code == 200
    assert (
        response.json()["final_notes"]
        == "Boa entrevista."
    )


def test_patch_rejects_different_session_id():
    assessment = build_assessment()

    create_response = client.post(
        "/api/v1/interview-sessions",
        json=assessment.model_dump(
            mode="json",
        ),
    )

    assert create_response.status_code == 201

    session = create_response.json()

    original_session_id = (
        session["session_id"]
    )

    session["session_id"] = (
        "11111111-1111-1111-1111-111111111111"
    )

    response = client.patch(
        (
            "/api/v1/interview-sessions/"
            f"{original_session_id}"
        ),
        json=session,
    )

    assert response.status_code == 422