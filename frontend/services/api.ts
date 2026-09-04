import { CandidateAssessment } from "@/types/assessment";

const API_BASE_URL = "http://127.0.0.1:8000";

export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

type ApiErrorResponse = {
  detail?: string;
};

async function getErrorMessage(
  response: Response,
): Promise<string> {
  try {
    const body =
      (await response.json()) as ApiErrorResponse;

    if (body.detail) {
      return body.detail;
    }
  } catch {
    // A resposta pode não possuir JSON válido.
  }

  return "Não foi possível processar a solicitação.";
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(
    `${API_BASE_URL}/health`,
  );

  if (!response.ok) {
    throw new Error(
      "Não foi possível acessar a API.",
    );
  }

  return response.json();
}

export async function createAssessment(
  jobDescription: string,
  resume: File,
): Promise<CandidateAssessment> {
  const formData = new FormData();

  formData.append(
    "job_description",
    jobDescription,
  );

  formData.append(
    "resume",
    resume,
  );

  const response = await fetch(
    `${API_BASE_URL}/api/v1/assessments`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const message =
      await getErrorMessage(response);

    throw new Error(message);
  }

  return response.json();
}