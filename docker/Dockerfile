FROM alpine:3.11.3
RUN apk update && apk add --no-cache supervisor lighttpd ffmpeg python3 aria2
COPY ./conf/lighttpd.conf /etc/lighttpd/lighttpd.conf
COPY ./conf/aria2.conf /aria2.conf
COPY ./src /var/www/localhost/htdocs/
COPY ./conf/supervisor.ini /etc/supervisord.conf
EXPOSE 80
ENTRYPOINT ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]