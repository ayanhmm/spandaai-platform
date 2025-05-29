# Stage 1: Build React App
FROM node:18 AS build
WORKDIR /app
COPY . .
RUN npm install && npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# Copy Nginx Config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy Built React App
COPY --from=build /app/dist /usr/share/nginx/html

# ✅ Copy env.sh to container
COPY env.sh /docker-entrypoint.d/env.sh
RUN chmod +x /docker-entrypoint.d/env.sh

# ✅ Run env.sh before starting Nginx
CMD ["/bin/sh", "-c", "/docker-entrypoint.d/env.sh && nginx -g 'daemon off;'"]