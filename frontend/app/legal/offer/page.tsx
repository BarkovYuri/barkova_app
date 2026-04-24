import { fetchAPI } from "../../../lib/api";
import type { LegalDocument } from "../../../lib/types";

export default async function OfferPage() {
  const documents = ((await fetchAPI("/legal")) || []) as LegalDocument[];
  const document = documents.find((item) => item.doc_type === "offer");

  return (
    <main className="min-h-screen bg-white px-6 py-12">
      <div className="mx-auto max-w-4xl">
        <p className="text-sm font-medium uppercase tracking-[0.2em] text-sky-600">
          Юридическая информация
        </p>
        <h1 className="mt-3 text-4xl font-semibold text-gray-900">
          {document?.title || "Оферта"}
        </h1>

        {document?.version ? (
          <p className="mt-4 text-sm text-gray-500">Версия: {document.version}</p>
        ) : null}

        <div className="prose prose-gray mt-8 max-w-none whitespace-pre-line text-gray-700">
          {document?.content || "Документ пока не добавлен."}
        </div>
      </div>
    </main>
  );
}