"use client";

import { FormEvent, useEffect, useState } from "react";

import {
  createAssessment,
  getHealth,
  HealthResponse,
} from "@/services/api";

import {
  CandidateAssessment,
  InterviewQuestion,
  RiskAssessment,
  SkillAssessment,
} from "@/types/assessment";

type SkillSectionProps = {
  title: string;
  skills: SkillAssessment[];
};


function SkillSection({
  title,
  skills,
}: SkillSectionProps) {
  if (skills.length === 0) {
    return null;
  }

  return (
    <section className="rounded-xl bg-white p-6 shadow-sm">
      <h2 className="text-xl font-bold text-gray-900">
        {title}
      </h2>

      <div className="mt-6 space-y-4">
        {skills.map((skill) => (
          <article
            key={`${skill.type}-${skill.name}`}
            className="rounded-lg border border-gray-200 p-5"
          >
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h3 className="font-semibold text-gray-900">
                  {skill.name}
                </h3>

                <p className="mt-1 text-sm text-gray-500">
                  Confiança: {skill.confidence}
                  {" · "}
                  Status: {skill.status}
                </p>
              </div>

              <div className="rounded-lg bg-gray-100 px-4 py-2 text-center">
                <span className="text-xl font-bold text-gray-900">
                  {skill.score}
                </span>

                <span className="text-sm text-gray-500">
                  /5
                </span>
              </div>
            </div>

            <p className="mt-4 text-sm leading-6 text-gray-700">
              {skill.justification}
            </p>

            {skill.evidence.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-800">
                  Evidências
                </p>

                <ul className="mt-2 space-y-2">
                  {skill.evidence.map(
                    (evidence, index) => (
                      <li
                        key={`${skill.name}-evidence-${index}`}
                        className="rounded-md bg-gray-50 p-3 text-sm text-gray-700"
                      >
                        <p>
                          {evidence.text}
                        </p>

                        <p className="mt-1 text-xs text-gray-500">
                          Fonte: {evidence.source}
                          {evidence.source_reference
                            ? ` · ${evidence.source_reference}`
                            : ""}
                          {evidence.page
                            ? ` · página ${evidence.page}`
                            : ""}
                        </p>
                      </li>
                    ),
                  )}
                </ul>
              </div>
            )}

            {skill.evidence.length === 0 && (
              <p className="mt-4 text-sm italic text-gray-500">
                Nenhuma evidência documental identificada.
              </p>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}

type InterviewQuestionsSectionProps = {
  questions: InterviewQuestion[];
};

function InterviewQuestionsSection({
  questions,
}: InterviewQuestionsSectionProps) {
  if (questions.length === 0) {
    return null;
  }

  return (
    <section className="rounded-xl bg-white p-6 shadow-sm">
      <h2 className="text-xl font-bold text-gray-900">
        Perguntas para a entrevista
      </h2>

      <p className="mt-2 text-sm text-gray-600">
        Perguntas sugeridas a partir das competências e
        evidências identificadas no assessment.
      </p>

      <div className="mt-6 space-y-4">
        {questions.map((question, index) => (
          <article
            key={`${question.competency}-${index}`}
            className="rounded-lg border border-gray-200 p-5"
          >
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
                {question.category}
              </span>

              <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
                Prioridade: {question.priority}
              </span>
            </div>

            <p className="mt-4 text-sm font-medium text-gray-500">
              {question.competency}
            </p>

            <p className="mt-2 text-base font-semibold leading-7 text-gray-900">
              {question.question}
            </p>

            <div className="mt-4">
              <p className="text-sm font-medium text-gray-800">
                Por que perguntar
              </p>

              <p className="mt-1 text-sm leading-6 text-gray-700">
                {question.reason}
              </p>
            </div>

            {question.follow_up && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-800">
                  Pergunta complementar
                </p>

                <p className="mt-1 text-sm leading-6 text-gray-700">
                  {question.follow_up}
                </p>
              </div>
            )}

            {question.what_to_observe.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-800">
                  O que observar
                </p>

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
        ))}
      </div>
    </section>
  );
}


type RisksSectionProps = {
  risks: RiskAssessment[];
};

function RisksSection({
  risks,
}: RisksSectionProps) {
  if (risks.length === 0) {
    return null;
  }

  return (
    <section className="rounded-xl bg-white p-6 shadow-sm">
      <h2 className="text-xl font-bold text-gray-900">
        Pontos para validação
      </h2>

      <p className="mt-2 text-sm text-gray-600">
        Itens que merecem atenção durante a entrevista.
        Um risco documental não significa ausência da
        competência.
      </p>

      <div className="mt-6 space-y-4">
        {risks.map((risk, index) => (
          <article
            key={`${risk.competency}-${index}`}
            className="rounded-lg border border-gray-200 p-5"
          >
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
                {risk.category}
              </span>

              <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
                Nível: {risk.level}
              </span>
            </div>

            <h3 className="mt-4 font-semibold text-gray-900">
              {risk.title}
            </h3>

            <p className="mt-1 text-sm text-gray-500">
              Competência: {risk.competency}
            </p>

            <p className="mt-4 text-sm leading-6 text-gray-700">
              {risk.description}
            </p>

            {risk.evidence.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-800">
                  Evidências relacionadas
                </p>

                <ul className="mt-2 space-y-2">
                  {risk.evidence.map(
                    (evidence, evidenceIndex) => (
                      <li
                        key={`${risk.competency}-evidence-${evidenceIndex}`}
                        className="rounded-md bg-gray-50 p-3 text-sm text-gray-700"
                      >
                        {evidence.text}
                      </li>
                    ),
                  )}
                </ul>
              </div>
            )}

            {risk.validation_question && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-800">
                  Como validar
                </p>

                <p className="mt-1 text-sm leading-6 text-gray-700">
                  {risk.validation_question}
                </p>
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}

type AssessmentConclusionProps = {
  comments: string[];
  recommendation: CandidateAssessment["recommendation"];
};

function AssessmentConclusion({
  comments,
  recommendation,
}: AssessmentConclusionProps) {
  return (
    <section className="rounded-xl bg-white p-6 shadow-sm">
      <h2 className="text-xl font-bold text-gray-900">
        Conclusão do assessment
      </h2>

      {comments.length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold text-gray-900">
            Comentários para o entrevistador
          </h3>

          <ul className="mt-3 space-y-2">
            {comments.map((comment, index) => (
              <li
                key={`comment-${index}`}
                className="rounded-lg bg-gray-50 p-4 text-sm leading-6 text-gray-700"
              >
                {comment}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-8">
        <h3 className="font-semibold text-gray-900">
          Recomendações
        </h3>

        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-gray-200 p-4">
            <p className="text-sm font-semibold text-gray-900">
              Curto prazo
            </p>

            <p className="mt-2 text-sm leading-6 text-gray-700">
              {recommendation.short_term}
            </p>
          </div>

          <div className="rounded-lg border border-gray-200 p-4">
            <p className="text-sm font-semibold text-gray-900">
              Médio prazo
            </p>

            <p className="mt-2 text-sm leading-6 text-gray-700">
              {recommendation.medium_term}
            </p>
          </div>

          <div className="rounded-lg border border-gray-200 p-4">
            <p className="text-sm font-semibold text-gray-900">
              Longo prazo
            </p>

            <p className="mt-2 text-sm leading-6 text-gray-700">
              {recommendation.long_term}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const [health, setHealth] =
    useState<HealthResponse | null>(null);

  const [healthError, setHealthError] =
    useState(false);

  const [jobDescription, setJobDescription] =
    useState("");

  const [resume, setResume] =
    useState<File | null>(null);

  const [assessment, setAssessment] =
    useState<CandidateAssessment | null>(null);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [submitError, setSubmitError] =
    useState<string | null>(null);


  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealthError(true));
  }, []);


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setSubmitError(null);
    setAssessment(null);

    if (!jobDescription.trim()) {
      setSubmitError(
        "Informe a descrição da vaga.",
      );

      return;
    }

    if (!resume) {
      setSubmitError(
        "Selecione o currículo do candidato.",
      );

      return;
    }

    try {
      setIsSubmitting(true);

      const result =
        await createAssessment(
          jobDescription,
          resume,
        );

      setAssessment(result);
    } catch (error) {
      if (error instanceof Error) {
        setSubmitError(error.message);
      } else {
        setSubmitError(
          "Não foi possível processar o assessment.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }


  return (
    <main className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-5xl px-6 py-10">
        <header>
          <h1 className="text-3xl font-bold text-gray-900">
            AI Interview Copilot
          </h1>

          <p className="mt-2 text-gray-600">
            Analise a aderência entre uma vaga e o
            currículo de um candidato.
          </p>

          <div className="mt-4 text-sm">
            {health && (
              <span className="text-green-700">
                API conectada · {health.service} ·
                v{health.version}
              </span>
            )}

            {healthError && (
              <span className="text-red-600">
                API indisponível
              </span>
            )}

            {!health && !healthError && (
              <span className="text-gray-500">
                Verificando API...
              </span>
            )}
          </div>
        </header>


        <section className="mt-10 rounded-xl bg-white p-6 shadow-sm">
          <form
            onSubmit={handleSubmit}
            className="space-y-6"
          >
            <div>
              <label
                htmlFor="job-description"
                className="block text-sm font-medium text-gray-800"
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
                className="mt-2 w-full rounded-lg border border-gray-300 p-3 text-sm text-gray-900 outline-none focus:border-gray-500"
                placeholder="Cole aqui a descrição completa da vaga..."
              />
            </div>


            <div>
              <label
                htmlFor="resume"
                className="block text-sm font-medium text-gray-800"
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
                className="mt-2 block w-full text-sm text-gray-700"
              />

              <p className="mt-2 text-xs text-gray-500">
                Formatos aceitos: TXT, PDF e DOCX.
              </p>
            </div>


            {submitError && (
              <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
                {submitError}
              </div>
            )}


            <button
              type="submit"
              disabled={isSubmitting}
              className="rounded-lg bg-gray-900 px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting
                ? "Analisando..."
                : "Analisar candidato"}
            </button>
          </form>
        </section>


        {assessment && (
          <div className="mt-8 space-y-8">
            <section className="rounded-xl bg-white p-6 shadow-sm">
              <p className="text-sm font-medium text-gray-500">
                Assessment concluído
              </p>

              <h2 className="mt-2 text-2xl font-bold text-gray-900">
                {assessment.candidate_name ??
                  "Candidato não identificado"}
              </h2>

              <p className="mt-1 text-gray-600">
                {assessment.job_title}
              </p>

              <div className="mt-6">
                <span className="text-4xl font-bold text-gray-900">
                  {assessment.adherence_percentage.toFixed(2)}%
                </span>

                <p className="mt-1 text-sm text-gray-500">
                  Aderência documental à vaga
                </p>
              </div>

              <p className="mt-6 leading-7 text-gray-700">
                {assessment.summary}
              </p>
            </section>

            <SkillSection
              title="Hard Skills"
              skills={assessment.hard_skills}
            />

            <SkillSection
              title="Soft Skills"
              skills={assessment.soft_skills}
            />

            <SkillSection
              title="Tecnologias"
              skills={assessment.technologies}
            />

            <InterviewQuestionsSection
              questions={assessment.questions}
            />

            <RisksSection
              risks={assessment.risks}
            />

            <AssessmentConclusion
              comments={assessment.interviewer_comments}
              recommendation={assessment.recommendation}
            />
          </div>
        )}
      </div>
    </main>
  );
}