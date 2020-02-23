FROM ffmpeg:3.2-alpine
RUN apk update && apk add --no-cache supervisor lighttpd python3 aria2
COPY ./conf/lighttpd.conf /etc/lighttpd/lighttpd.conf
COPY ./conf/aria2.conf /aria2.conf
COPY ./src /var/www/localhost/htdocs/
COPY ./conf/supervisor.ini /etc/supervisor.d/
EXPOSE 80
CMD while true; do sleep 2; df -h; done
#ENTRYPOINT ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]