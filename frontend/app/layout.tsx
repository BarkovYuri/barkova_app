import "./globals.css";
import type { Metadata, Viewport } from "next";
import { Manrope, Spectral } from "next/font/google";
import Header from "../components/layout/Header";
import Footer from "../components/layout/Footer";

const manrope = Manrope({
  subsets: ["latin", "cyrillic"],
  display: "swap",
  variable: "--font-sans",
  weight: ["400", "500", "600", "700", "800"],
});

const spectral = Spectral({
  subsets: ["latin", "cyrillic"],
  display: "swap",
  variable: "--font-heading",
  weight: ["400", "500", "600", "700"],
});

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://doctor-barkova.ru";
const SITE_NAME = "Кабинет врача-инфекциониста";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_NAME} · Барькова Елена Игоревна`,
    template: `%s · ${SITE_NAME}`,
  },
  description:
    "Онлайн-консультации и очный приём врача-инфекциониста. Запись через сайт за 30 секунд, подтверждение в Telegram или VK.",
  keywords: [
    "врач инфекционист",
    "онлайн консультация инфекциониста",
    "телемедицина",
    "запись к врачу онлайн",
    "Баркова",
    "Томск",
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
      "Онлайн-консультации и очный приём врача-инфекциониста. Запись через сайт за 30 секунд.",
  },
  twitter: {
    card: "summary_large_image",
    title: `${SITE_NAME} · Баркова Елена Игоревна`,
    description:
      "Онлайн-консультации и очный приём врача-инфекциониста. Запись за 30 секунд.",
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
  icons: {
    icon: "/favicon.ico",
  },
  category: "health",
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
    <html lang="ru" className={`${manrope.variable} ${spectral.variable}`}>
      <body className="font-sans bg-neutral-0 text-neutral-900 antialiased">
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
