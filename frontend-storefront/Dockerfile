# Storefront (Next.js), built and served via Bun.
# Single-stage for now; standalone/runtime optimization is a later task.
FROM oven/bun:1

WORKDIR /app

# Install the whole bun workspace: root lockfile + every member's manifest.
COPY package.json bun.lock /app/
COPY frontend-dashboard/package.json /app/frontend-dashboard/
COPY frontend-storefront/package.json /app/frontend-storefront/

WORKDIR /app/frontend-storefront
RUN bun install

COPY ./frontend-storefront /app/frontend-storefront
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN bun run build

EXPOSE 3000
CMD ["bun", "run", "start"]
