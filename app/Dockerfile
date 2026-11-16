FROM node:24-alpine AS build
WORKDIR /app
RUN npm install -g corepack && corepack enable
COPY ["package.json", "yarn.lock", ".yarnrc.yml", "./"]
RUN yarn install --immutable
COPY . .
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# SPA fallback for react-router
RUN printf 'server {\n  listen 4173;\n  root /usr/share/nginx/html;\n  location / { try_files $uri /index.html; }\n}\n' > /etc/nginx/conf.d/default.conf
EXPOSE 4173
