# Frontend multi-stage Dockerfile (Vite + React)

# Build stage
FROM node:18-alpine AS builder
WORKDIR /app

# Copy package metadata first to leverage caching
COPY frontend/package*.json ./
COPY frontend/ ./

RUN npm install
RUN npm run build

# Production stage: serve static files with nginx
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
