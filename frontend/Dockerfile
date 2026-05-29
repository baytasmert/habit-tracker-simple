FROM nginx:1.25-alpine

# Default NGINX site config'i değiştir
COPY nginx.conf /etc/nginx/conf.d/default.conf

# HTML/CSS/JS dosyaları
COPY index.html register.html dashboard.html /usr/share/nginx/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost/healthz || exit 1
