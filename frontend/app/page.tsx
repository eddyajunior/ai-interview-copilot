"use client";

import { useEffect, useState } from "react";
import { getHealth, HealthResponse } from "@/services/api";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setError(true));
  }, []);

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center px-6">
        <h1 className="text-4xl font-bold text-gray-900">
          AI Interview Copilot
        </h1>

        <p className="mt-4 text-lg text-gray-600">
          Plataforma inteligente de apoio a entrevistas.
        </p>

        <p className="mt-2 text-sm text-gray-500">
          MVP v0.1.0
        </p>

        <div className="mt-8">
          {health && (
            <p className="text-sm text-gray-700">
              API conectada · {health.service} · v{health.version}
            </p>
          )}

          {error && (
            <p className="text-sm text-red-600">
              API indisponível
            </p>
          )}

          {!health && !error && (
            <p className="text-sm text-gray-500">
              Verificando API...
            </p>
          )}
        </div>
      </div>
    </main>
  );
}