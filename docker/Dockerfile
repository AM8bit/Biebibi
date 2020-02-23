FROM alpine:3.11.3
RUN apk update && apk add --no-cache supervisor lighttpd ffmpeg python3 aria2
COPY conf /
COPY conf /etc/lighttpd/lighttpd.conf
COPY conf /etc/supervisord.conf
COPY web/src /var/www/localhost/htdocs/
EXPOSE 80
ENTRYPOINT ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]