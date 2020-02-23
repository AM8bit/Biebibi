FROM jrottenberg/ffmpeg:4.1-alpine
RUN apk update && apk add --no-cache supervisor lighttpd python3 aria2
COPY ./conf/lighttpd.conf /etc/lighttpd/lighttpd.conf
COPY ./conf/aria2.conf /aria2.conf
COPY ./src /var/www/localhost/htdocs/
COPY ./conf/supervisor.ini /etc/supervisor.d/
RUN chown -R lighttpd. /var/www/localhost/
EXPOSE 80
ENTRYPOINT ["/usr/bin/supervisord","-n", "-c","/etc/supervisord.conf"]
