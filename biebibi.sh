#!/usr/bin/env bash
trap "printf ""\nExiting...""; exit 0;" INT
USER_AGENT="User-Agent: Mozilla/5.0  AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13C75 MicroMessenger/6.5.15 NetType/4G Language/zh_CN"
rm -rf caches/*; mkdir -p download caches
function m4s_get() {
  body=`curl "$1" -H "$USER_AGENT" \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.5' --compressed`
  title=$(perl -ne 'print "$1" if /"title":"(.*?)"/'<<<$body)
  media_find=$(perl -ne 'print join "|", @av if @av=/"(video|audio)":\[{"id":\d+,"baseUrl":"(.*?)"/g'<<<$body)
  IFS='|' read -ra M4S_INFO <<<"$media_find"
  read -r video_m4s audio_m4s <<<$(echo ${M4S_INFO[1]} ${M4S_INFO[3]})
  printf "video m4s: ${video_m4s}\naudio m4s: ${audio_m4s}\n"
  for m4s_link in $video_m4s $audio_m4s; do
    curl $m4s_link -H "$USER_AGENT" \
            -H 'Accept: */*' \
            -H 'Accept-Language: en-US,en;q=0.5' \
            -H 'Referer: https://www.bilibili.com/' \
            --compressed -o "caches/$(echo $m4s_link | md5).m4s"
  done
  ffmpeg -i "caches/$(echo $video_m4s | md5).m4s" \
         -i "caches/$(echo $audio_m4s | md5).m4s" -c copy "download/${title}.mp4"
  if [[ $? == 0 ]];then echo "[ download/$title.mp4 ] saved!"; fi
}
if [ -z "$1" ];then printf "usage: \n $0 https://www.bilibili.com/video/avXXXXXXX/\n"; exit 1; fi
m4s_get $1
