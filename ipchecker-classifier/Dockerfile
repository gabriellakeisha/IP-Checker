FROM --platform=linux/amd64 node:18-alpine

WORKDIR /app

# copy package files
COPY package*.json ./

# install dependencies
RUN npm install --production

# copy source code
COPY src/ ./src/

EXPOSE 80

ENV PORT=80

# start the server
CMD ["node", "src/server.js"]