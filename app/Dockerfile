FROM node:24-alpine AS build
WORKDIR /app
RUN npm install -g corepack && corepack enable
COPY ["package.json", "yarn.lock", ".yarnrc.yml", "./"]
RUN yarn install --immutable
COPY . .
RUN yarn build

FROM nginx:alpine
# Same path as the former vite preview image, so existing config.json mounts keep working
COPY --from=build /app/dist /app/dist
RUN printf 'server {\n  listen 4173;\n  root /app/dist;\n  location = /config.json { try_files $uri =404; }\n  location / { try_files $uri /index.html; }\n}\n' > /etc/nginx/conf.d/default.conf
EXPOSE 4173
