# ---------- STAGE 1: Builder ----------
    FROM node:20-bookworm-slim AS builder

    WORKDIR /app
    
    ARG NEXT_PUBLIC_VK_APP_ID
    ENV NEXT_PUBLIC_VK_APP_ID=${NEXT_PUBLIC_VK_APP_ID}
    ENV NEXT_TELEMETRY_DISABLED=1
    ENV NEXT_DISABLE_TURBOPACK=1
    
    # Копируем зависимости
    COPY package.json package-lock.json ./
    RUN npm install --legacy-peer-deps
    
    # Копируем весь фронтенд
    COPY . .
    
    # Собираем продакшн билд
    RUN npm run build
    
    # ---------- STAGE 2: Production ----------
    FROM node:20-bookworm-slim AS runner
    
    WORKDIR /app
    
    ENV NODE_ENV=production
    ENV NEXT_TELEMETRY_DISABLED=1
    
    # Копируем только необходимые файлы
    COPY package.json package-lock.json ./
    COPY --from=builder /app/node_modules ./node_modules
    COPY --from=builder /app/.next ./.next
    COPY --from=builder /app/public ./public
    
    EXPOSE 3000
    
    CMD ["npm", "start"]