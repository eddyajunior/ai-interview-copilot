"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  createAssessment,
  createInterviewSession,
  getHealth,
  HealthResponse,
  updateInterviewSession,
} from "@/services/api";

import {
  CandidateAssessment,
  InterviewQuestion,
  InterviewSession,
  RiskAssessment,
  SkillAssessment,
} from "@/types/assessment";


function getConfidenceLabel(
  confidence: string,
): string {
  const labels: Record<string, string> = {
    low: "Baixa",
    medium: "Média",
    high: "Alta",
  };

  return labels[confidence] ?? confidence;
}


function getPriorityLabel(
  priority: string,
): string {
  const labels: Record<string, string> = {
    low: "Baixa",
    medium: "Média",
    high: "Alta",
  };

  return labels[priority] ?? priority;
}


function getCategoryLabel(
  category: string,
): string {
  const labels: Record<string, string> = {
    hard_skill: "Hard Skill",
    soft_skill: "Soft Skill",
    technology: "Tecnologia",
    other: "Outro",
    evidence_gap: "Evidência ausente",
    limited_evidence: "Evidência limitada",
    validation_required: "Validação necessária",
  };

  return labels[category] ?? category;
}


function SkillCard({
  skill,
}: {
  skill: SkillAssessment;
}) {
  return (
    <article className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold">
            {skill.name}
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Confiança:{" "}
            {getConfidenceLabel(skill.confidence)}
          </p>

          <p className="mt-1 text-sm text-gray-500">
            Status: {skill.status}
          </p>
        </div>

        <div className="rounded-xl border px-4 py-2 text-center">
          <p className="text-xs uppercase tracking-wide text-gray-500">
            Nota
          </p>

          <p className="text-2xl font-semibold">
            {skill.score}/5
          </p>
        </div>
      </div>

      <p className="mt-4 text-sm leading-6 text-gray-700">
        {skill.justification}
      </p>

      <div className="mt-5">
        <h4 className="text-sm font-semibold">
          Evidências
        </h4>

        {skill.evidence.length > 0 ? (
          <div className="mt-2 space-y-3">
            {skill.evidence.map(
              (evidence, index) => (
                <div
                  key={`${skill.name}-evidence-${index}`}
                  className="rounded-xl bg-gray-50 p-3"
                >
                  <p className="text-sm text-gray-700">
                    {evidence.text}
                  </p>

                  <p className="mt-2 text-xs text-gray-500">
                    Fonte: {evidence.source}
                    {evidence.source_reference
                      ? ` — ${evidence.source_reference}`
                      : ""}
                  </p>
                </div>
              ),
            )}
          </div>
        ) : (
          <p className="mt-2 text-sm text-gray-500">
            Nenhuma evidência documental
            identificada.
          </p>
        )}
      </div>
    </article>
  );
}


function QuestionCard({
  question,
  index,
}: {
  question: InterviewQuestion;
  index: number;
}) {
  return (
    <article className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full border px-3 py-1 text-xs">
          Pergunta {index + 1}
        </span>

        <span className="rounded-full border px-3 py-1 text-xs">
          {getCategoryLabel(question.category)}
        </span>

        <span className="rounded-full border px-3 py-1 text-xs">
          Prioridade:{" "}
          {getPriorityLabel(question.priority)}
        </span>
      </div>

      <p className="mt-4 text-sm font-medium text-gray-500">
        {question.competency}
      </p>

      <p className="mt-2 text-lg font-medium leading-7">
        {question.question}
      </p>

      <div className="mt-5">
        <h4 className="text-sm font-semibold">
          Por que perguntar
        </h4>

        <p className="mt-1 text-sm leading-6 text-gray-700">
          {question.reason}
        </p>
      </div>

      {question.follow_up && (
        <div className="mt-5">
          <h4 className="text-sm font-semibold">
            Follow-up
          </h4>

          <p className="mt-1 text-sm leading-6 text-gray-700">
            {question.follow_up}
          </p>
        </div>
      )}

      {question.what_to_observe.length > 0 && (
        <div className="mt-5">
          <h4 className="text-sm font-semibold">
            O que observar
          </h4>

          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-gray-700">
            {question.what_to_observe.map(
              (item, itemIndex) => (
                <li
                  key={`${question.competency}-observe-${itemIndex}`}
                >
                  {item}
                </li>
              ),
            )}
          </ul>
        </div>
      )}
    </article>
  );
}


function RiskCard({
  risk,
}: {
  risk: RiskAssessment;
}) {
  return (
    <article className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full border px-3 py-1 text-xs">
          {getCategoryLabel(risk.category)}
        </span>

        <span className="rounded-full border px-3 py-1 text-xs">
          Nível: {getPriorityLabel(risk.level)}
        </span>
      </div>

      <p className="mt-4 text-sm font-medium text-gray-500">
        {risk.competency}
      </p>

      <h3 className="mt-1 text-lg font-semibold">
        {risk.title}
      </h3>

      <p className="mt-3 text-sm leading-6 text-gray-700">
        {risk.description}
      </p>

      {risk.evidence.length > 0 && (
        <div className="mt-5">
          <h4 className="text-sm font-semibold">
            Evidências documentais relacionadas
          </h4>

          <div className="mt-2 space-y-2">
            {risk.evidence.map(
              (evidence, index) => (
                <div
                  key={`${risk.competency}-risk-evidence-${index}`}
                  className="rounded-xl bg-gray-50 p-3"
                >
                  <p className="text-sm text-gray-700">
                    {evidence.text}
                  </p>
                </div>
              ),
            )}
          </div>
        </div>
      )}

      {risk.validation_question && (
        <div className="mt-5 rounded-xl bg-gray-50 p-4">
          <h4 className="text-sm font-semibold">
            Sugestão para validação
          </h4>

          <p className="mt-1 text-sm leading-6 text-gray-700">
            {risk.validation_question}
          </p>
        </div>
      )}
    </article>
  );
}


export default function Home() {
  const [
    health,
    setHealth,
  ] = useState<HealthResponse | null>(null);

  const [
    healthError,
    setHealthError,
  ] = useState<string | null>(null);

  const [
    jobDescription,
    setJobDescription,
  ] = useState("");

  const [
    resume,
    setResume,
  ] = useState<File | null>(null);

  const [
    assessment,
    setAssessment,
  ] = useState<CandidateAssessment | null>(
    null,
  );

  const [
    isSubmitting,
    setIsSubmitting,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(null);

  const [
    interviewSession,
    setInterviewSession,
  ] = useState<InterviewSession | null>(
    null,
  );

  const [
    currentQuestionIndex,
    setCurrentQuestionIndex,
  ] = useState(0);

  const [
    isStartingInterview,
    setIsStartingInterview,
  ] = useState(false);

  const [
    interviewError,
    setInterviewError,
  ] = useState<string | null>(null);

  const [
    isSavingInterview,
    setIsSavingInterview,
  ] = useState(false);

  const [
    interviewSaveError,
    setInterviewSaveError,
  ] = useState<string | null>(null);


  useEffect(() => {
    async function loadHealth() {
      try {
        const response = await getHealth();

        setHealth(response);
        setHealthError(null);
      } catch {
        setHealthError(
          "Backend indisponível.",
        );
      }
    }

    loadHealth();
  }, []);


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!jobDescription.trim()) {
      setError(
        "Informe a descrição da vaga.",
      );
      return;
    }

    if (!resume) {
      setError(
        "Selecione o currículo do candidato.",
      );
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setAssessment(null);
    setInterviewSession(null);
    setInterviewError(null);
    setInterviewSaveError(null);
    setCurrentQuestionIndex(0);

    try {
      const result = await createAssessment(
        jobDescription,
        resume,
      );

      setAssessment(result);
    } catch (submitError) {
      if (submitError instanceof Error) {
        setError(submitError.message);
      } else {
        setError(
          "Não foi possível gerar o assessment.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }


  async function handleStartInterview() {
    if (!assessment) {
      return;
    }

    setIsStartingInterview(true);
    setInterviewError(null);
    setInterviewSaveError(null);

    try {
      const session =
        await createInterviewSession(
          assessment,
        );

      setInterviewSession(session);
      setCurrentQuestionIndex(0);
    } catch (startError) {
      if (startError instanceof Error) {
        setInterviewError(
          startError.message,
        );
      } else {
        setInterviewError(
          "Não foi possível iniciar a entrevista.",
        );
      }
    } finally {
      setIsStartingInterview(false);
    }
  }


  async function saveInterviewSession(
    session: InterviewSession,
  ) {
    setIsSavingInterview(true);
    setInterviewSaveError(null);

    try {
      const savedSession =
        await updateInterviewSession(session);

      setInterviewSession(savedSession);
    } catch (saveError) {
      if (saveError instanceof Error) {
        setInterviewSaveError(
          saveError.message,
        );
      } else {
        setInterviewSaveError(
          "Não foi possível salvar a entrevista.",
        );
      }
    } finally {
      setIsSavingInterview(false);
    }
  }


  function handlePreviousQuestion() {
    setCurrentQuestionIndex((current) =>
      Math.max(current - 1, 0),
    );
  }


  function handleNextQuestion() {
    if (!interviewSession) {
      return;
    }

    setCurrentQuestionIndex((current) =>
      Math.min(
        current + 1,
        interviewSession.questions.length - 1,
      ),
    );
  }


  function handleQuestionNotesChange(
    value: string,
  ) {
    setInterviewSession((currentSession) => {
      if (!currentSession) {
        return currentSession;
      }

      const questions = [
        ...currentSession.questions,
      ];

      questions[currentQuestionIndex] = {
        ...questions[currentQuestionIndex],
        interviewer_notes: value,
      };

      return {
        ...currentSession,
        questions,
      };
    });
  }


  function handleResponseSummaryChange(
    value: string,
  ) {
    setInterviewSession((currentSession) => {
      if (!currentSession) {
        return currentSession;
      }

      const questions = [
        ...currentSession.questions,
      ];

      questions[currentQuestionIndex] = {
        ...questions[currentQuestionIndex],
        response_summary: value,
      };

      return {
        ...currentSession,
        questions,
      };
    });
  }


  function handleEvaluationChange(
    value:
      | "not_evaluated"
      | "below_expectation"
      | "partially_meets"
      | "meets"
      | "exceeds",
  ) {
    setInterviewSession((currentSession) => {
      if (!currentSession) {
        return currentSession;
      }

      const questions = [
        ...currentSession.questions,
      ];

      questions[currentQuestionIndex] = {
        ...questions[currentQuestionIndex],
        evaluation: value,
      };

      return {
        ...currentSession,
        questions,
      };
    });
  }


  function handleEvidenceStrengthChange(
    value:
      | "not_evaluated"
      | "low"
      | "medium"
      | "high",
  ) {
    setInterviewSession((currentSession) => {
      if (!currentSession) {
        return currentSession;
      }

      const questions = [
        ...currentSession.questions,
      ];

      questions[currentQuestionIndex] = {
        ...questions[currentQuestionIndex],
        evidence_strength: value,
      };

      return {
        ...currentSession,
        questions,
      };
    });
  }


  async function handleMarkQuestionAsAsked() {
    if (!interviewSession) {
      return;
    }

    const questions = [
      ...interviewSession.questions,
    ];

    const currentQuestion =
      questions[currentQuestionIndex];

    questions[currentQuestionIndex] = {
      ...currentQuestion,
      status: "asked",
    };

    const updatedSession: InterviewSession = {
      ...interviewSession,
      questions,
    };

    setInterviewSession(updatedSession);

    await saveInterviewSession(
      updatedSession,
    );
  }


  async function handleSkipQuestion() {
    if (!interviewSession) {
      return;
    }

    const questions = [
      ...interviewSession.questions,
    ];

    questions[currentQuestionIndex] = {
      ...questions[currentQuestionIndex],
      status: "skipped",
    };

    const updatedSession: InterviewSession = {
      ...interviewSession,
      questions,
    };

    setInterviewSession(updatedSession);

    await saveInterviewSession(
      updatedSession,
    );
  }


  function handleFinalNotesChange(
    value: string,
  ) {
    setInterviewSession((currentSession) => {
      if (!currentSession) {
        return currentSession;
      }

      return {
        ...currentSession,
        final_notes: value,
      };
    });
  }


  async function handleCompleteInterview() {
    if (!interviewSession) {
      return;
    }

    const hasPendingQuestions =
      interviewSession.questions.some(
        (question) =>
          question.status === "pending",
      );

    if (hasPendingQuestions) {
      return;
    }

    const updatedSession: InterviewSession = {
      ...interviewSession,
      completed_at: new Date().toISOString(),
    };

    setInterviewSession(updatedSession);

    await saveInterviewSession(
      updatedSession,
    );
  }


  return (
    <main className="min-h-screen bg-gray-50 text-gray-950">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <header className="mb-10">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm font-medium uppercase tracking-wider text-gray-500">
                AI Interview Copilot
              </p>

              <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
                Assessment de candidatos
              </h1>

              <p className="mt-3 max-w-3xl text-gray-600">
                Analise currículo e vaga, identifique
                evidências, pontos para validação e
                perguntas para apoiar a entrevista.
              </p>
            </div>

            <div className="rounded-xl border bg-white px-4 py-3 shadow-sm">
              <p className="text-xs uppercase tracking-wide text-gray-500">
                Backend
              </p>

              {health ? (
                <p className="mt-1 text-sm font-medium">
                  Conectado
                </p>
              ) : healthError ? (
                <p className="mt-1 text-sm font-medium text-red-600">
                  Indisponível
                </p>
              ) : (
                <p className="mt-1 text-sm text-gray-500">
                  Verificando...
                </p>
              )}
            </div>
          </div>
        </header>


        <section className="rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">
            Novo assessment
          </h2>

          <p className="mt-1 text-sm text-gray-600">
            Informe a descrição da vaga e envie
            o currículo do candidato.
          </p>

          <form
            onSubmit={handleSubmit}
            className="mt-6 space-y-6"
          >
            <div>
              <label
                htmlFor="job-description"
                className="text-sm font-medium"
              >
                Descrição da vaga
              </label>

              <textarea
                id="job-description"
                value={jobDescription}
                onChange={(event) =>
                  setJobDescription(
                    event.target.value,
                  )
                }
                rows={12}
                placeholder="Cole aqui a descrição completa da vaga..."
                className="mt-2 w-full rounded-xl border p-4 text-sm outline-none focus:ring-2 focus:ring-gray-900"
              />
            </div>

            <div>
              <label
                htmlFor="resume"
                className="text-sm font-medium"
              >
                Currículo
              </label>

              <input
                id="resume"
                type="file"
                accept=".txt,.pdf,.docx"
                onChange={(event) =>
                  setResume(
                    event.target.files?.[0] ??
                      null,
                  )
                }
                className="mt-2 block w-full rounded-xl border bg-white p-3 text-sm"
              />

              <p className="mt-2 text-xs text-gray-500">
                Formatos aceitos: TXT, PDF e DOCX.
              </p>
            </div>

            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-4">
                <p className="text-sm text-red-700">
                  {error}
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="rounded-lg bg-black px-6 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting
                ? "Analisando..."
                : "Gerar assessment"}
            </button>
          </form>
        </section>


        {assessment && (
          <div className="mt-10 space-y-8">
            <section className="rounded-2xl border bg-white p-6 shadow-sm">
              <div className="grid gap-6 md:grid-cols-[1fr_auto]">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    Candidato
                  </p>

                  <h2 className="mt-1 text-2xl font-semibold">
                    {assessment.candidate_name ??
                      "Não identificado"}
                  </h2>

                  <p className="mt-3 text-sm font-medium text-gray-500">
                    Vaga
                  </p>

                  <p className="mt-1 text-lg">
                    {assessment.job_title}
                  </p>
                </div>

                <div className="rounded-2xl border p-5 text-center">
                  <p className="text-xs uppercase tracking-wide text-gray-500">
                    Aderência
                  </p>

                  <p className="mt-2 text-4xl font-bold">
                    {assessment.adherence_percentage.toFixed(
                      1,
                    )}
                    %
                  </p>
                </div>
              </div>

              <div className="mt-6 border-t pt-6">
                <h3 className="text-sm font-semibold">
                  Resumo
                </h3>

                <p className="mt-2 leading-7 text-gray-700">
                  {assessment.summary}
                </p>
              </div>
            </section>


            <section>
              <h2 className="text-2xl font-semibold">
                Pontos fortes
              </h2>

              {assessment.strengths.length > 0 ? (
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  {assessment.strengths.map(
                    (strength, index) => (
                      <div
                        key={`strength-${index}`}
                        className="rounded-xl border bg-white p-4 shadow-sm"
                      >
                        <p className="text-sm leading-6">
                          {strength}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              ) : (
                <p className="mt-3 text-sm text-gray-500">
                  Nenhum ponto forte identificado.
                </p>
              )}
            </section>


            <section>
              <h2 className="text-2xl font-semibold">
                Pontos de menor aderência documental
              </h2>

              <p className="mt-1 text-sm text-gray-600">
                Estes itens representam menor
                evidência no currículo e não
                necessariamente ausência de
                competência.
              </p>

              {assessment.weaknesses.length > 0 ? (
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  {assessment.weaknesses.map(
                    (weakness, index) => (
                      <div
                        key={`weakness-${index}`}
                        className="rounded-xl border bg-white p-4 shadow-sm"
                      >
                        <p className="text-sm leading-6">
                          {weakness}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              ) : (
                <p className="mt-3 text-sm text-gray-500">
                  Nenhum ponto identificado.
                </p>
              )}
            </section>


            <section>
              <h2 className="text-2xl font-semibold">
                Hard Skills
              </h2>

              <div className="mt-4 grid gap-5 lg:grid-cols-2">
                {assessment.hard_skills.map(
                  (skill) => (
                    <SkillCard
                      key={`hard-${skill.name}`}
                      skill={skill}
                    />
                  ),
                )}
              </div>
            </section>


            <section>
              <h2 className="text-2xl font-semibold">
                Soft Skills
              </h2>

              <div className="mt-4 grid gap-5 lg:grid-cols-2">
                {assessment.soft_skills.map(
                  (skill) => (
                    <SkillCard
                      key={`soft-${skill.name}`}
                      skill={skill}
                    />
                  ),
                )}
              </div>
            </section>


            <section>
              <h2 className="text-2xl font-semibold">
                Tecnologias
              </h2>

              <div className="mt-4 grid gap-5 lg:grid-cols-2">
                {assessment.technologies.map(
                  (skill) => (
                    <SkillCard
                      key={`technology-${skill.name}`}
                      skill={skill}
                    />
                  ),
                )}
              </div>
            </section>


            <section>
              <h2 className="text-2xl font-semibold">
                Perguntas para entrevista
              </h2>

              <p className="mt-1 text-sm text-gray-600">
                Perguntas sugeridas com base na
                relação entre a vaga e as
                evidências encontradas no currículo.
              </p>

              <div className="mt-4 grid gap-5">
                {assessment.questions.map(
                  (question, index) => (
                    <QuestionCard
                      key={`question-${index}`}
                      question={question}
                      index={index}
                    />
                  ),
                )}
              </div>
            </section>


            <section>
              <h2 className="text-2xl font-semibold">
                Pontos para validação
              </h2>

              <p className="mt-1 text-sm text-gray-600">
                Estes itens representam pontos que
                merecem confirmação durante a
                entrevista. Ausência de evidência
                documental não significa ausência
                da competência.
              </p>

              <div className="mt-4 grid gap-5 lg:grid-cols-2">
                {assessment.risks.map(
                  (risk, index) => (
                    <RiskCard
                      key={`risk-${index}`}
                      risk={risk}
                    />
                  ),
                )}
              </div>
            </section>


            <section className="rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold">
                Comentários ao entrevistador
              </h2>

              {assessment.interviewer_comments.length >
              0 ? (
                <ul className="mt-4 list-disc space-y-2 pl-5 text-sm leading-6 text-gray-700">
                  {assessment.interviewer_comments.map(
                    (comment, index) => (
                      <li key={`comment-${index}`}>
                        {comment}
                      </li>
                    ),
                  )}
                </ul>
              ) : (
                <p className="mt-3 text-sm text-gray-500">
                  Nenhum comentário adicional.
                </p>
              )}
            </section>


            <section className="rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold">
                Recomendações
              </h2>

              <div className="mt-5 grid gap-5 md:grid-cols-3">
                <div className="rounded-xl bg-gray-50 p-4">
                  <p className="text-sm font-semibold">
                    Curto prazo
                  </p>

                  <p className="mt-2 text-sm leading-6 text-gray-700">
                    {
                      assessment.recommendation
                        .short_term
                    }
                  </p>
                </div>

                <div className="rounded-xl bg-gray-50 p-4">
                  <p className="text-sm font-semibold">
                    Médio prazo
                  </p>

                  <p className="mt-2 text-sm leading-6 text-gray-700">
                    {
                      assessment.recommendation
                        .medium_term
                    }
                  </p>
                </div>

                <div className="rounded-xl bg-gray-50 p-4">
                  <p className="text-sm font-semibold">
                    Longo prazo
                  </p>

                  <p className="mt-2 text-sm leading-6 text-gray-700">
                    {
                      assessment.recommendation
                        .long_term
                    }
                  </p>
                </div>
              </div>
            </section>


            <section className="rounded-2xl border bg-white p-6 shadow-sm">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2 className="text-xl font-semibold">
                    Entrevista
                  </h2>

                  <p className="mt-1 max-w-2xl text-sm text-gray-600">
                    Inicie a entrevista para
                    registrar evidências e
                    observações coletadas durante a
                    conversa com o candidato.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handleStartInterview}
                  disabled={
                    isStartingInterview ||
                    interviewSession !== null
                  }
                  className="rounded-lg bg-black px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isStartingInterview
                    ? "Iniciando..."
                    : interviewSession
                      ? "Entrevista iniciada"
                      : "Iniciar entrevista"}
                </button>
              </div>

              {interviewError && (
                <p className="mt-3 text-sm text-red-600">
                  {interviewError}
                </p>
              )}
            </section>
          </div>
        )}


        {interviewSession && (
          <section className="mt-10 rounded-2xl border bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-5 border-b pb-6 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">
                  Interview Workspace
                </p>

                <h2 className="mt-1 text-2xl font-semibold">
                  {interviewSession.candidate_name ??
                    "Candidato"}
                </h2>

                <p className="mt-1 text-gray-600">
                  {interviewSession.job_title}
                </p>
              </div>

              <div className="flex gap-3">
                <div className="rounded-xl border px-4 py-3">
                  <p className="text-xs uppercase tracking-wide text-gray-500">
                    Perguntas
                  </p>

                  <p className="mt-1 text-xl font-semibold">
                    {
                      interviewSession.questions
                        .length
                    }
                  </p>
                </div>

                <div className="rounded-xl border px-4 py-3">
                  <p className="text-xs uppercase tracking-wide text-gray-500">
                    Respondidas
                  </p>

                  <p className="mt-1 text-xl font-semibold">
                    {
                      interviewSession.questions.filter(
                        (question) =>
                          question.status ===
                          "asked",
                      ).length
                    }
                  </p>
                </div>
              </div>
            </div>


            {interviewSession.questions.length >
            0 ? (
              <div className="mt-6">
                {(() => {
                  const currentQuestion =
                    interviewSession.questions[
                      currentQuestionIndex
                    ];

                  const treatedQuestions =
                    interviewSession.questions.filter(
                      (question) =>
                        question.status !==
                        "pending",
                    ).length;

                  const progressPercentage =
                    interviewSession.questions
                      .length > 0
                      ? (
                          treatedQuestions /
                          interviewSession.questions
                            .length
                        ) * 100
                      : 0;

                  return (
                    <>
                      <div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">
                            Progresso da entrevista
                          </span>

                          <span className="font-medium">
                            {treatedQuestions}/
                            {
                              interviewSession
                                .questions.length
                            }
                          </span>
                        </div>

                        <div className="mt-2 h-2 overflow-hidden rounded-full bg-gray-200">
                          <div
                            className="h-full bg-black transition-all"
                            style={{
                              width: `${progressPercentage}%`,
                            }}
                          />
                        </div>

                        {isSavingInterview && (
                          <p className="mt-2 text-xs text-gray-500">
                            Salvando entrevista...
                          </p>
                        )}

                        {interviewSaveError && (
                          <p className="mt-2 text-xs text-red-600">
                            {interviewSaveError}
                          </p>
                        )}
                      </div>


                      <div className="mt-6 flex items-center justify-between gap-4">
                        <div>
                          <p className="text-sm text-gray-500">
                            Pergunta{" "}
                            {currentQuestionIndex +
                              1}{" "}
                            de{" "}
                            {
                              interviewSession
                                .questions.length
                            }
                          </p>

                          <p className="mt-1 text-sm font-medium">
                            {
                              currentQuestion.competency
                            }
                          </p>
                        </div>

                        <span className="rounded-full border px-3 py-1 text-xs">
                          {currentQuestion.status ===
                          "asked"
                            ? "Respondida"
                            : currentQuestion.status ===
                                "skipped"
                              ? "Ignorada"
                              : "Pendente"}
                        </span>
                      </div>


                      <div className="mt-5 rounded-xl border p-5">
                        <p className="text-lg font-medium leading-relaxed">
                          {
                            currentQuestion.question
                          }
                        </p>
                      </div>


                      <div className="mt-6">
                        <label
                          htmlFor="interviewer-notes"
                          className="text-sm font-medium"
                        >
                          Observações do
                          entrevistador
                        </label>

                        <p className="mt-1 text-xs text-gray-500">
                          Registre evidências,
                          exemplos apresentados pelo
                          candidato e observações
                          relevantes.
                        </p>

                        <textarea
                          id="interviewer-notes"
                          rows={6}
                          value={
                            currentQuestion.interviewer_notes ??
                            ""
                          }
                          onChange={(event) =>
                            handleQuestionNotesChange(
                              event.target.value,
                            )
                          }
                          disabled={
                            interviewSession.completed_at !==
                            null
                          }
                          placeholder="Ex.: apresentou exemplo concreto de liderança durante uma migração crítica..."
                          className="mt-3 w-full rounded-xl border p-4 text-sm outline-none focus:ring-2 focus:ring-gray-900 disabled:bg-gray-50"
                        />
                      </div>


                      <div className="mt-6">
                        <label
                          htmlFor="response-summary"
                          className="text-sm font-medium"
                        >
                          Resumo da resposta
                        </label>

                        <p className="mt-1 text-xs text-gray-500">
                          Registre uma síntese
                          objetiva do que o candidato
                          respondeu.
                        </p>

                        <textarea
                          id="response-summary"
                          rows={4}
                          value={
                            currentQuestion.response_summary ??
                            ""
                          }
                          onChange={(event) =>
                            handleResponseSummaryChange(
                              event.target.value,
                            )
                          }
                          disabled={
                            interviewSession.completed_at !==
                            null
                          }
                          placeholder="Ex.: explicou que liderou a migração dividindo o trabalho por domínio e definindo critérios de rollback."
                          className="mt-3 w-full rounded-xl border p-4 text-sm outline-none focus:ring-2 focus:ring-gray-900 disabled:bg-gray-50"
                        />
                      </div>


                      <div className="mt-6 grid gap-5 md:grid-cols-2">
                        <div>
                          <label
                            htmlFor="response-evaluation"
                            className="text-sm font-medium"
                          >
                            Avaliação da resposta
                          </label>

                          <p className="mt-1 text-xs text-gray-500">
                            Avalie a resposta em
                            relação ao esperado para
                            a competência.
                          </p>

                          <select
                            id="response-evaluation"
                            value={
                              currentQuestion.evaluation
                            }
                            onChange={(event) =>
                              handleEvaluationChange(
                                event.target
                                  .value as
                                  | "not_evaluated"
                                  | "below_expectation"
                                  | "partially_meets"
                                  | "meets"
                                  | "exceeds",
                              )
                            }
                            disabled={
                              interviewSession.completed_at !==
                              null
                            }
                            className="mt-3 w-full rounded-xl border bg-white p-3 text-sm disabled:bg-gray-50"
                          >
                            <option value="not_evaluated">
                              Não avaliada
                            </option>

                            <option value="below_expectation">
                              Abaixo do esperado
                            </option>

                            <option value="partially_meets">
                              Atende parcialmente
                            </option>

                            <option value="meets">
                              Atende
                            </option>

                            <option value="exceeds">
                              Supera o esperado
                            </option>
                          </select>
                        </div>


                        <div>
                          <label
                            htmlFor="evidence-strength"
                            className="text-sm font-medium"
                          >
                            Força da evidência
                          </label>

                          <p className="mt-1 text-xs text-gray-500">
                            Indique quão concreta
                            foi a evidência
                            apresentada pelo
                            candidato.
                          </p>

                          <select
                            id="evidence-strength"
                            value={
                              currentQuestion.evidence_strength
                            }
                            onChange={(event) =>
                              handleEvidenceStrengthChange(
                                event.target
                                  .value as
                                  | "not_evaluated"
                                  | "low"
                                  | "medium"
                                  | "high",
                              )
                            }
                            disabled={
                              interviewSession.completed_at !==
                              null
                            }
                            className="mt-3 w-full rounded-xl border bg-white p-3 text-sm disabled:bg-gray-50"
                          >
                            <option value="not_evaluated">
                              Não avaliada
                            </option>

                            <option value="low">
                              Baixa
                            </option>

                            <option value="medium">
                              Média
                            </option>

                            <option value="high">
                              Alta
                            </option>
                          </select>
                        </div>
                      </div>


                      <div className="mt-6 border-t pt-6">
                        {currentQuestion.status !==
                          "skipped" &&
                          (currentQuestion.evaluation ===
                            "not_evaluated" ||
                            currentQuestion.evidence_strength ===
                              "not_evaluated") && (
                            <p className="mb-4 text-xs text-gray-500">
                              Informe a avaliação da
                              resposta e a força da
                              evidência antes de
                              marcar a pergunta como
                              respondida.
                            </p>
                          )}

                        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                          <button
                            type="button"
                            onClick={
                              handlePreviousQuestion
                            }
                            disabled={
                              currentQuestionIndex ===
                                0 ||
                              isSavingInterview
                            }
                            className="rounded-lg border px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40"
                          >
                            Anterior
                          </button>

                          <div className="flex flex-col gap-3 sm:flex-row">
                            <button
                              type="button"
                              onClick={
                                handleSkipQuestion
                              }
                              disabled={
                                currentQuestion.status ===
                                  "asked" ||
                                currentQuestion.status ===
                                  "skipped" ||
                                isSavingInterview ||
                                interviewSession.completed_at !==
                                  null
                              }
                              className="rounded-lg border px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-40"
                            >
                              {currentQuestion.status ===
                              "skipped"
                                ? "Ignorada"
                                : "Ignorar pergunta"}
                            </button>

                            <button
                              type="button"
                              onClick={
                                handleMarkQuestionAsAsked
                              }
                              disabled={
                                currentQuestion.status ===
                                  "asked" ||
                                currentQuestion.status ===
                                  "skipped" ||
                                currentQuestion.evaluation ===
                                  "not_evaluated" ||
                                currentQuestion.evidence_strength ===
                                  "not_evaluated" ||
                                isSavingInterview ||
                                interviewSession.completed_at !==
                                  null
                              }
                              className="rounded-lg border px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-40"
                            >
                              {currentQuestion.status ===
                              "asked"
                                ? "Respondida"
                                : "Marcar como respondida"}
                            </button>

                            <button
                              type="button"
                              onClick={
                                handleNextQuestion
                              }
                              disabled={
                                currentQuestionIndex ===
                                  interviewSession
                                    .questions.length -
                                    1 ||
                                isSavingInterview
                              }
                              className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-40"
                            >
                              Próxima
                            </button>
                          </div>
                        </div>
                      </div>
                    </>
                  );
                })()}
              </div>
            ) : (
              <p className="mt-6 text-sm text-gray-600">
                Nenhuma pergunta disponível para
                esta entrevista.
              </p>
            )}


            <div className="mt-8 border-t pt-8">
              <h3 className="text-lg font-semibold">
                Conclusão da entrevista
              </h3>

              <p className="mt-1 text-sm text-gray-600">
                Registre observações gerais antes
                de concluir a entrevista.
              </p>

              <textarea
                rows={5}
                value={
                  interviewSession.final_notes ??
                  ""
                }
                onChange={(event) =>
                  handleFinalNotesChange(
                    event.target.value,
                  )
                }
                disabled={
                  interviewSession.completed_at !==
                  null
                }
                placeholder="Ex.: candidato apresentou boa profundidade técnica e exemplos concretos de liderança..."
                className="mt-4 w-full rounded-xl border p-4 text-sm outline-none focus:ring-2 focus:ring-gray-900 disabled:bg-gray-50"
              />

              {(() => {
                const pendingQuestions =
                  interviewSession.questions.filter(
                    (question) =>
                      question.status ===
                      "pending",
                  ).length;

                const completed =
                  interviewSession.completed_at !==
                  null;

                return (
                  <div className="mt-5 flex flex-col gap-4 rounded-xl bg-gray-50 p-4 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      {completed ? (
                        <>
                          <p className="font-medium">
                            Entrevista concluída
                          </p>

                          <p className="mt-1 text-sm text-gray-600">
                            Todas as perguntas foram
                            tratadas e a entrevista
                            foi finalizada.
                          </p>
                        </>
                      ) : pendingQuestions > 0 ? (
                        <>
                          <p className="font-medium">
                            Entrevista em andamento
                          </p>

                          <p className="mt-1 text-sm text-gray-600">
                            {pendingQuestions}{" "}
                            {pendingQuestions === 1
                              ? "pergunta ainda está pendente."
                              : "perguntas ainda estão pendentes."}
                          </p>
                        </>
                      ) : (
                        <>
                          <p className="font-medium">
                            Entrevista pronta para
                            conclusão
                          </p>

                          <p className="mt-1 text-sm text-gray-600">
                            Todas as perguntas foram
                            tratadas.
                          </p>
                        </>
                      )}
                    </div>

                    <button
                      type="button"
                      onClick={
                        handleCompleteInterview
                      }
                      disabled={
                        completed ||
                        pendingQuestions > 0 ||
                        isSavingInterview
                      }
                      className="rounded-lg bg-black px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      {completed
                        ? "Entrevista concluída"
                        : isSavingInterview
                          ? "Salvando..."
                          : "Concluir entrevista"}
                    </button>
                  </div>
                );
              })()}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}