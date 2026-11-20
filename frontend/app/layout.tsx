import "./globals.css";
import type { Metadata, Viewport } from "next";
import { Manrope, Spectral } from "next/font/google";
import Script from "next/script";
import { Suspense } from "react";
import { MetrikaRouteTracker } from "../components/common/MetrikaRouteTracker";
import Header from "../components/layout/Header";
import Footer from "../components/layout/Footer";
import MobileStickyCta from "../components/layout/MobileStickyCta";
import { METRIKA_ID } from "../lib/metrika";

const manrope = Manrope({
  subsets: ["latin", "cyrillic"],
  display: "swap",
  variable: "--font-sans",
  // Только реально используемые начертания: каждое — отдельный файл шрифта.
  weight: ["400", "500", "600", "700"],
});

const spectral = Spectral({
  subsets: ["latin", "cyrillic"],
  display: "swap",
  variable: "--font-heading",
  // Заголовки используют только 600 и 700.
  weight: ["600", "700"],
});

// Все страницы рендерятся на запрос: шапка берёт профиль врача из API, а
// при сборке в CI бэкенд недоступен. Данные API при этом кэшируются на
// минуту в lib/api.ts, так что нагрузка на Django не растёт.
export const revalidate = 0;

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://doctor-barkova.ru";
const SITE_NAME = "Кабинет врача-инфекциониста";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_NAME} · Баркова Елена Игоревна`,
    template: `%s · ${SITE_NAME}`,
  },
  description:
    "Врач-инфекционист в Томске: очный приём и информационные онлайн-разборы. Запись на онлайн-разбор через сайт, подтверждение в VK.",
  keywords: [
    "врач инфекционист Томск",
    "онлайн-разбор у инфекциониста",
    "запись к инфекционисту Томск",
    "Баркова Елена Игоревна",
    "вирусный гепатит Томск",
    "TORCH-инфекции",
    "лямблиоз лечение",
    "длительная температура причины",
    "увеличенные лимфоузлы врач",
    "паразитология Томск",
    "вакцинация взрослых Томск",
    "СибГМУ инфекционист",
  ],
  authors: [{ name: "Баркова Елена Игоревна" }],
  applicationName: SITE_NAME,
  generator: "Next.js",
  referrer: "origin-when-cross-origin",
  openGraph: {
    type: "website",
    locale: "ru_RU",
    url: SITE_URL,
    siteName: SITE_NAME,
    title: `${SITE_NAME} · Баркова Елена Игоревна`,
    description:
      "Онлайн-разборы и очный приём врача-инфекциониста. Запись через сайт за 30 секунд.",
  },
  twitter: {
    card: "summary_large_image",
    title: `${SITE_NAME} · Баркова Елена Игоревна`,
    description:
      "Онлайн-разборы и очный приём врача-инфекциониста. Запись за 30 секунд.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: SITE_URL,
  },
  // Иконки автоматически берутся из app/icon.svg, app/icon.tsx,
  // app/apple-icon.tsx — Next.js строит метаданные сам.
  category: "health",
  // Verification — заполняются после регистрации в Search Console
  // и Яндекс.Вебмастере. Коды кладутся в .env прода как
  // NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION / NEXT_PUBLIC_YANDEX_VERIFICATION.
  verification: {
    google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION || undefined,
    yandex: process.env.NEXT_PUBLIC_YANDEX_VERIFICATION || undefined,
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0e7490" },
  ],
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru" className={`${manrope.variable} ${spectral.variable} scroll-pt-24`}>
      <body className="font-sans bg-neutral-0 text-neutral-900 antialiased">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:bg-primary-700 focus:text-white focus:px-4 focus:py-2 focus:rounded-lg focus:shadow-lg"
        >
          Перейти к содержанию
        </a>
        <Header />
        {children}
        <Footer />
        <MobileStickyCta />

        {/* Яндекс Метрика — код из кабинета Метрики. afterInteractive не
            блокирует гидратацию и успевает зафиксировать первый просмотр.
            Переходы внутри сайта отправляет MetrikaRouteTracker. */}
        {METRIKA_ID ? (
          <>
            <Script id="yandex-metrika" strategy="afterInteractive">
              {`(function(m,e,t,r,i,k,a){
    m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
    m[i].l=1*new Date();
    for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
    k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=${METRIKA_ID}', 'ym');
ym(${METRIKA_ID}, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});`}
            </Script>
            <noscript>
              <div>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`https://mc.yandex.ru/watch/${METRIKA_ID}`}
                  style={{ position: "absolute", left: "-9999px" }}
                  alt=""
                />
              </div>
            </noscript>
            <Suspense fallback={null}>
              <MetrikaRouteTracker />
            </Suspense>
          </>
        ) : null}
      </body>
    </html>
  );
}
