# Build context is the repo root (see docker-compose.dev.yml) so this can
# COPY the workspace packages/ the app depends on.
FROM node:24-slim AS build
WORKDIR /repo

COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
COPY packages/shared-types/package.json packages/shared-types/package.json
COPY packages/api-client/package.json packages/api-client/package.json
COPY packages/ontology-client/package.json packages/ontology-client/package.json
COPY packages/ui-components/package.json packages/ui-components/package.json
RUN npm ci

COPY packages/ packages/
COPY apps/web/ apps/web/
RUN npm run build --workspace packages/shared-types \
 && npm run build --workspace packages/api-client \
 && npm run build --workspace packages/ontology-client \
 && npm run build --workspace packages/ui-components \
 && npm run build --workspace apps/web

FROM nginx:alpine AS runtime
COPY --from=build /repo/apps/web/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK CMD wget -qO- http://localhost/ || exit 1
