![image](https://raw.githubusercontent.com/AM8bit/Biebibi/master/example.png)

terminal usage 
--------------


The operating environment requires ffmpeg, you may need these steps.

Debian: 
```shell
apt-get -y install curl ffmpeg
```

CentOS: 
```shell
yum install -y curl ffmpeg
```

MacOs: 
```shell
brew install ffmpeg
```
```shell
chmod +x ./biebibi.sh
./biebibi.sh https://www.bilibili.com/video/avXXXXXXX/
```

good luck～

Also web version
================

The web version is a standalone version and currently uses lighttpd + CGI as the operating environment.
You can deploy it with docker

Docker depoly
-------------

```shell
git clone https://github.com/AM8bit/Biebibi.git
cd docker
docker build -t biebibi_web .
docker run -d -it -p 8080:80 --name biebibi --rm biebibi_web
```
okay, visit port 8080 now




