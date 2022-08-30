FROM node:15.5.1 AS build

#RUN npm install -g http-server

WORKDIR /app
COPY package.json ./
# RUN npm install
COPY . .
# RUN npm run build -- No se porque el build en este proyecto no funciona, lo cual obliga a hacer el build manual antes de generar los contenedores
 
FROM nginx:1.19.0-alpine AS prod-stage
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

