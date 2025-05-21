FROM node:16-alpine as build

WORKDIR /app

# نسخ ملفات التكوين
COPY package*.json ./
RUN npm install

# نسخ باقي الملفات
COPY . .

# بناء التطبيق
RUN npm run build

# مرحلة الإنتاج
FROM nginx:alpine

# نسخ الملفات المبنية إلى مجلد nginx
COPY --from=build /app/build /usr/share/nginx/html

# نسخ تكوين nginx المخصص
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
