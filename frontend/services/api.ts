export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch("http://127.0.0.1:8000/health");

  if (!response.ok) {
    throw new Error("Não foi possível acessar a API.");
  }

  return response.json();
}