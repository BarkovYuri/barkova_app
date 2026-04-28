/**
 * Хелперы для работы с редактируемым контентом сайта.
 *
 * Все секции сайта (услуги, FAQ, шаги, подход, бейджи) и простые тексты
 * (через SiteBlock по ключам) загружаются из Django backend и могут
 * редактироваться врачом через Django-админку.
 *
 * Если API недоступен или данные пустые — функции возвращают [] / null.
 * Компоненты, использующие эти данные, должны иметь fallback.
 */

import { fetchAPI } from "./api";
import type {
  ApproachItem,
  FaqItem,
  HowItWorksStep,
  Service,
  SiteBlock,
  TransportItem,
  TrustBadge,
} from "./types";

// ----- Простые тексты (key/value) -----

export async function loadSiteBlocks(): Promise<Map<string, SiteBlock>> {
  const data = (await fetchAPI("/blocks")) as SiteBlock[] | null;
  const map = new Map<string, SiteBlock>();
  if (Array.isArray(data)) {
    for (const block of data) {
      map.set(block.key, block);
    }
  }
  return map;
}

/**
 * Хелпер: достать текст по ключу с fallback'ом.
 * Использование:
 *   const blocks = await loadSiteBlocks();
 *   const heroSubtitle = textOr(blocks, "hero.subtitle", "Дефолтный текст");
 */
export function textOr(
  blocks: Map<string, SiteBlock>,
  key: string,
  fallback: string
): string {
  const block = blocks.get(key);
  return block?.content?.trim() || fallback;
}

// ----- Структурированные коллекции -----

export async function loadServices(): Promise<Service[]> {
  const data = (await fetchAPI("/services")) as Service[] | null;
  return Array.isArray(data) ? data : [];
}

export async function loadHowItWorksSteps(): Promise<HowItWorksStep[]> {
  const data = (await fetchAPI("/how-it-works")) as HowItWorksStep[] | null;
  return Array.isArray(data) ? data : [];
}

export async function loadFaqItems(): Promise<FaqItem[]> {
  const data = (await fetchAPI("/faq")) as FaqItem[] | null;
  return Array.isArray(data) ? data : [];
}

export async function loadApproachItems(): Promise<ApproachItem[]> {
  const data = (await fetchAPI("/approach")) as ApproachItem[] | null;
  return Array.isArray(data) ? data : [];
}

export async function loadTrustBadges(): Promise<TrustBadge[]> {
  const data = (await fetchAPI("/trust-badges")) as TrustBadge[] | null;
  return Array.isArray(data) ? data : [];
}

export async function loadTransportItems(): Promise<TransportItem[]> {
  const data = (await fetchAPI("/transport")) as TransportItem[] | null;
  return Array.isArray(data) ? data : [];
}
