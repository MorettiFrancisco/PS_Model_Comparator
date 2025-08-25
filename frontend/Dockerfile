# Dockerfile para el frontend Vue.js
FROM node:18-alpine as build-stage

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de dependencias primero (mejor cache)
COPY package*.json ./

# Instala las dependencias (sin --only=production para incluir devDependencies)
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copia el resto del código fuente
COPY . .

# Construye la aplicación para producción
RUN npm run build

# Usa nginx para servir los archivos estáticos
FROM nginx:alpine

# Copia los archivos construidos al directorio de nginx
COPY --from=0 /app/dist /usr/share/nginx/html

# Copia configuración personalizada de nginx si es necesaria
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expone el puerto 80
EXPOSE 80

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]
