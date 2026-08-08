# syntax=docker/dockerfile:1
# ------------------------------------------------------------------------------------
# InsightUlasan — frontend statis
# Build React lalu disajikan nginx. Node tidak ikut ke image akhir: yang dibutuhkan saat
# melayani hanyalah berkas statis hasil build.
# ------------------------------------------------------------------------------------
FROM node:22-slim AS build
WORKDIR /src
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM nginx:1.27-alpine
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/dist /usr/share/nginx/html
EXPOSE 80
