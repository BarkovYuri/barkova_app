import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #155e75 0%, #0e7490 100%)",
          color: "#ffffff",
          borderRadius: 36,
          fontFamily: "system-ui, -apple-system, sans-serif",
          fontWeight: 700,
        }}
      >
        <div
          style={{
            position: "relative",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 110,
            height: 110,
          }}
        >
          {/* Медицинский крест */}
          <div
            style={{
              position: "absolute",
              width: 28,
              height: 110,
              background: "#ffffff",
              borderRadius: 6,
            }}
          />
          <div
            style={{
              position: "absolute",
              width: 110,
              height: 28,
              background: "#ffffff",
              borderRadius: 6,
            }}
          />
        </div>
      </div>
    ),
    { ...size },
  );
}
