FROM node:20-alpine
WORKDIR /app
RUN npm install -g corepack
COPY ["package.json", "yarn.lock", "./"]
RUN yarn install
COPY . .
EXPOSE 5173
CMD [ "yarn", "run", "dev", "--host" , "0.0.0.0" ]
