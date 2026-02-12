"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { TOKEN_STORAGE_KEY } from "../lib/catalogia";

export default function LoginPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [error, setError] = useState<string | null>(null);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedToken = token.trim();
    if (!normalizedToken) {
      setError("Debes ingresar un token valido.");
      return;
    }

    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, normalizedToken);
    setError(null);
    router.push("/upload");
  }

  return (
    <section className="card">
      <h2>Sesion de catalogador (MVP)</h2>
      <p>
        Ingresa el token de entorno (por ejemplo, `CATALOGER_TOKEN`) para usar
        endpoints protegidos.
      </p>
      <form onSubmit={onSubmit} className="formStack">
        <label>
          Token
          <input
            type="password"
            name="token"
            placeholder="pega tu token aqui"
            value={token}
            onChange={(event) => setToken(event.target.value)}
          />
        </label>
        {error ? <p className="statusError">{error}</p> : null}
        <button type="submit">Ingresar</button>
      </form>
      <p>
        Continuar: <a href="/upload">Carga de archivo</a>
      </p>
    </section>
  );
}
