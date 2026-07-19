# Этап 1: Сборка Vue приложения
FROM node:18-alpine as build-stage

# Передаем API URL как переменную окружения для сборки
#ARG VUE_APP_API_URL
#ENV VUE_APP_API_URL=$VUE_APP_API_URL

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код
COPY . .

# Собираем проект для production
RUN npm run build

# Этап 2: Nginx для обслуживания статики
FROM nginx:stable-alpine as production-stage

# Копируем собранные файлы из первого этапа в nginx
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Копируем конфиг nginx (по умолчанию production, можно переопределить через --build-arg)
ARG NGINX_CONF=nginx.conf
COPY ${NGINX_CONF} /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
