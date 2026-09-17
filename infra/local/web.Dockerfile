# PKG-00 skeleton image: runs the minimum Next.js proof UI shell.
# Only the Phase 0 placeholder page exists; the 12 proof UI lands in Phase 11.
FROM node:20-slim

WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json* ./
RUN npm install
COPY apps/web ./

EXPOSE 3000
CMD ["npm", "run", "dev"]
