export type EvidenceSource =
  | "professional_summary"
  | "experience"
  | "education"
  | "certification"
  | "skill_section"
  | "job_description"
  | "other";

export type Evidence = {
  text: string;
  source: EvidenceSource;
  source_reference: string | null;
  page: number | null;
};

export type SkillType =
  | "hard_skill"
  | "soft_skill"
  | "technology";

export type ConfidenceLevel =
  | "low"
  | "medium"
  | "high";

export type SkillAssessment = {
  name: string;
  type: SkillType;
  score: number;
  evidence: Evidence[];
  justification: string;
  confidence: ConfidenceLevel;
  status: string;
};

export type InterviewQuestionCategory =
  | "hard_skill"
  | "soft_skill"
  | "technology"
  | "other";

export type InterviewQuestionPriority =
  | "low"
  | "medium"
  | "high";

export type InterviewQuestion = {
  category: InterviewQuestionCategory;
  competency: string;
  question: string;
  reason: string;
  priority: InterviewQuestionPriority;
  follow_up: string | null;
  what_to_observe: string[];
};

export type RiskLevel =
  | "low"
  | "medium"
  | "high";

export type RiskCategory =
  | "evidence_gap"
  | "limited_evidence"
  | "validation_required"
  | "other";

export type RiskAssessment = {
  competency: string;
  title: string;
  category: RiskCategory;
  level: RiskLevel;
  description: string;
  evidence: Evidence[];
  validation_question: string | null;
};

export type Recommendation = {
  short_term: string;
  medium_term: string;
  long_term: string;
};

export type CandidateAssessment = {
  candidate_name: string | null;
  job_title: string;
  summary: string;
  adherence_percentage: number;
  strengths: string[];
  weaknesses: string[];
  hard_skills: SkillAssessment[];
  soft_skills: SkillAssessment[];
  technologies: SkillAssessment[];
  questions: InterviewQuestion[];
  risks: RiskAssessment[];
  interviewer_comments: string[];
  recommendation: Recommendation;
};

export type InterviewQuestionStatus =
  | "pending"
  | "asked"
  | "skipped";

export type InterviewResponseEvaluation =
  | "not_evaluated"
  | "below_expectation"
  | "partially_meets"
  | "meets"
  | "exceeds";

export type InterviewEvidenceStrength =
  | "not_evaluated"
  | "low"
  | "medium"
  | "high";

export interface InterviewQuestionRecord {
  question_index: number;
  competency: string;
  question: string;

  status: InterviewQuestionStatus;

  interviewer_notes: string | null;
  response_summary: string | null;

  evaluation: InterviewResponseEvaluation;

  evidence_strength: InterviewEvidenceStrength;
}

export interface InterviewSession {
  session_id: string;

  candidate_name: string | null;
  job_title: string;

  started_at: string | null;
  completed_at: string | null;

  questions: InterviewQuestionRecord[];

  final_notes: string | null;
}