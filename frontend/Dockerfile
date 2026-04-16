FROM node:20-bookworm-slim AS builder

WORKDIR /app

ARG NEXT_PUBLIC_VK_APP_ID

ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_DISABLE_TURBOPACK=1
ENV NEXT_PUBLIC_VK_APP_ID=${NEXT_PUBLIC_VK_APP_ID}

COPY package.json package-lock.json ./
RUN npm install

COPY . .

RUN npm run build


FROM node:20-bookworm-slim AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_DISABLE_TURBOPACK=1

COPY package.json package-lock.json ./
RUN npm install --omit=dev

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "run", "start"]