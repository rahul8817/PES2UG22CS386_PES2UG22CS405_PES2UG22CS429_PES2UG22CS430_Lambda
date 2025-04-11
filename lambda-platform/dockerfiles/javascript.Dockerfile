FROM node:18-slim

WORKDIR /app

COPY function.javascript /app/function.js

CMD ["node", "function.js"]
