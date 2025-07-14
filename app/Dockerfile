FROM node:20-alpine
WORKDIR /app
RUN npm install -g corepack
COPY ["package.json", "yarn.lock", "./"]
RUN yarn install --frozen-lockfile
COPY . .
# Build the app for production
RUN yarn build
# Expose the port used by vite preview (default 4173)
EXPOSE 4173
# Run the production preview server
CMD ["yarn", "run", "preview", "--host", "0.0.0.0"]
