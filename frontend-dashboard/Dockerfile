# Stage 0, "build-stage", based on Bun, to build and compile the frontend-dashboard
FROM oven/bun:1 AS build-stage

WORKDIR /app

COPY package.json bun.lock /app/

COPY frontend-dashboard/package.json /app/frontend-dashboard/
COPY frontend-storefront/package.json /app/frontend-storefront/

WORKDIR /app/frontend-dashboard

RUN bun install

COPY ./frontend-dashboard /app/frontend-dashboard
ARG VITE_API_URL

RUN bun run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

COPY --from=build-stage /app/frontend-dashboard/dist/ /usr/share/nginx/html

COPY ./frontend-dashboard/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./frontend-dashboard/nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
