import { ImageResponse } from "next/og";

export const alt = "Кабинет врача-инфекциониста · Баркова Елена Игоревна";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/**
 * Фирменная OG-картинка для шаринга в Telegram, VK, WhatsApp,
 * Facebook и Twitter. Рендерится один раз и кэшируется.
 *
 * Применяется к ВСЕМ страницам, у которых в их metadata.openGraph.images
 * не задан собственный image. Для главной и /about — отдельные могут
 * задаваться позже (например, фото врача), пока единый бренд-ключ.
 */
export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          background:
            "linear-gradient(135deg, #155e75 0%, #0e7490 60%, #0e7490 100%)",
          color: "#ffffff",
          fontFamily: "system-ui, -apple-system, sans-serif",
          padding: 80,
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Декоративный glow */}
        <div
          style={{
            position: "absolute",
            top: -200,
            right: -200,
            width: 600,
            height: 600,
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(34, 211, 238, 0.45) 0%, transparent 70%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: -200,
            left: -200,
            width: 500,
            height: 500,
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(16, 185, 129, 0.25) 0%, transparent 70%)",
          }}
        />

        {/* Логотип-крест */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 24,
            position: "relative",
          }}
        >
          <div
            style={{
              position: "relative",
              width: 96,
              height: 96,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "rgba(255, 255, 255, 0.12)",
              borderRadius: 24,
              border: "2px solid rgba(255, 255, 255, 0.25)",
            }}
          >
            <div
              style={{
                position: "absolute",
                width: 22,
                height: 56,
                background: "#ffffff",
                borderRadius: 6,
              }}
            />
            <div
              style={{
                position: "absolute",
                width: 56,
                height: 22,
                background: "#ffffff",
                borderRadius: 6,
              }}
            />
          </div>
          <div
            style={{
              fontSize: 30,
              fontWeight: 600,
              opacity: 0.85,
              letterSpacing: -0.5,
            }}
          >
            Кабинет врача-инфекциониста
          </div>
        </div>

        {/* Главный заголовок */}
        <div
          style={{
            marginTop: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 20,
            position: "relative",
          }}
        >
          <div
            style={{
              fontSize: 88,
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: -2,
              maxWidth: 980,
            }}
          >
            Баркова Елена Игоревна
          </div>
          <div
            style={{
              fontSize: 36,
              fontWeight: 500,
              lineHeight: 1.3,
              opacity: 0.92,
              maxWidth: 900,
            }}
          >
            Онлайн-разборы и очный приём в&nbsp;Томске
          </div>
        </div>

        {/* Подвал с URL и CTA */}
        <div
          style={{
            marginTop: 32,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            position: "relative",
            paddingTop: 24,
            borderTop: "1px solid rgba(255, 255, 255, 0.2)",
          }}
        >
          <div style={{ fontSize: 24, opacity: 0.85, fontWeight: 500 }}>
            doctor-barkova.ru
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "16px 28px",
              background: "#ffffff",
              color: "#0e7490",
              borderRadius: 14,
              fontSize: 24,
              fontWeight: 700,
            }}
          >
            Записаться →
          </div>
        </div>
      </div>
    ),
    { ...size },
  );
}
