import { fetchAPI } from "../../../lib/api";
import type { LegalDocument } from "../../../lib/types";

export default async function PrivacyPage() {
  const documents = ((await fetchAPI("/legal")) || []) as LegalDocument[];
  const document = documents.find((item) => item.doc_type === "privacy");

  return (
    <main className="min-h-screen bg-neutral-0">
      <div className="container py-16 md:py-24 max-w-4xl">
        <span className="chip">Юридическая информация</span>
        <h1 className="mt-5 text-neutral-900">
          {document?.title || "Политика конфиденциальности"}
        </h1>

        {document?.version ? (
          <p className="mt-4 text-sm text-neutral-500">
            Версия: {document.version}
          </p>
        ) : null}

        <div className="mt-10 max-w-none whitespace-pre-line text-neutral-700 text-base-large leading-relaxed">
          {document?.content || "Документ пока не добавлен."}
        </div>
      </div>
    </main>
  );
}