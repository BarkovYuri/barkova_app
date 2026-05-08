import type { Metadata } from "next";

import { fetchAPI } from "../../../lib/api";
import type { LegalDocument } from "../../../lib/types";

export const revalidate = 300;

async function loadConsent(): Promise<LegalDocument | undefined> {
  const documents = ((await fetchAPI("/legal")) || []) as LegalDocument[];
  return documents.find((item) => item.doc_type === "consent");
}

export async function generateMetadata(): Promise<Metadata> {
  const document = await loadConsent();
  const title = document?.title || "Согласие на обработку персональных данных";
  const description =
    document?.content?.replace(/\s+/g, " ").trim().slice(0, 200) ||
    "Согласие на обработку персональных данных в соответствии с 152-ФЗ.";
  return {
    title,
    description,
    alternates: { canonical: "/legal/consent" },
    openGraph: { title, description, type: "article" },
  };
}

export default async function ConsentPage() {
  const document = await loadConsent();

  return (
    <main id="main" className="min-h-screen bg-neutral-0">
      <div className="container py-16 md:py-24 max-w-4xl">
        <span className="chip">Юридическая информация</span>
        <h1 className="mt-5 text-neutral-900">
          {document?.title || "Согласие на обработку персональных данных"}
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
