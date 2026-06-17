
FROM docker.io/library/httpd:2.4-alpine

COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf


RUN apk add --no-cache openssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /usr/local/apache2/conf/server.key \
    -out /usr/local/apache2/conf/server.crt \
    -subj "/C=MX/ST=NL/L=Guadalupe/O=KGPCo/CN=localhost"

EXPOSE 80
EXPOSE 443