FROM nginx:1.25-alpine

# NGINX 1.19+ otomatik /etc/nginx/templates/*.template dosyalarını
# envsubst ile process eder, /etc/nginx/conf.d/ altına yazar.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# HTML/CSS/JS dosyaları
COPY index.html login.html register.html dashboard.html /usr/share/nginx/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/

# Defaults (lokal docker-compose ve Railway override eder)
ENV PORT=80 \
    BACKEND_URL=http://backend:8000

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:$PORT/healthz || exit 1
