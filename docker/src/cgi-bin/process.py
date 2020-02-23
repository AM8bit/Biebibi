#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cgi
import gzip
import hashlib
import json
import os
import re
import socket
import urllib.request
from xmlrpc import client

USER_AGENT = 'Mozilla/5.0  AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13C75 MicroMessenger/6.5.15 NetType/4G Language/zh_CN'
cache_root = os.path.realpath('../caches/')
download_dir = '../download'
if not os.path.isdir(download_dir): os.mkdir(download_dir)


def p_gzip_data(resp):
    if 'gzip' == resp.headers.get('Content-Encoding'):
        try:
            return gzip.decompress(resp.read()).decode('utf-8')
        except (OSError, IOError):  # Not a gzip file
            pass


def add_Download_job(gid_group):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', 7000))
    except socket.error as msg:
        print(msg)
        exit(1)
    try:
        message = gid_group
        sock.send(message.encode())
    finally:
        sock.close()


def is_cached(v_md5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', 7000))
    except socket.error as msg:
        print(msg)
        exit(1)
    try:
        sock.send(b'is_convertd:' + v_md5.encode())
        rev = sock.recv(2)
        if rev.decode() == 'ok':
            return True
    finally:
        sock.close()


def respone(log = '', **kw):
    print(json.dumps({
        'succ': True,
        'data': kw['data'] if kw['data'] else [],
        'log': log
    }))
    exit()


def response_err(log):
    print(json.dumps({
        'succ': False,
        'error': log
    }))
    exit()


def get_vmd5(path):
    return os.path.splitext(os.path.basename(path))[0]


def task_status(vgid, agid):
    video_down_status = s.aria2.tellStatus(vgid)
    audio_down_status = s.aria2.tellStatus(agid)
    total_size = (int(video_down_status['totalLength']) + int(audio_down_status['totalLength']))
    down_speed = (int(video_down_status['downloadSpeed']) + int(audio_down_status['downloadSpeed']))
    completed_len = (int(video_down_status['completedLength']) + int(audio_down_status['completedLength']))
    status = 'complete'
    cached = False
    if video_down_status['status'] != 'complete' or audio_down_status['status'] != 'complete':
        status = 'waiting'
    if status == 'complete':
        v_md5 = get_vmd5(video_down_status['files'][0]['path'])
        if is_cached(v_md5): cached = True
    return {
        'total_size': total_size,
        'down_speed': down_speed,
        'bytes': completed_len,
        'status': status,
        'vgid': vgid,
        'agid': agid,
        'cached': cached
    }


def flv_task_status(vgid):
    video_down_status = s.aria2.tellStatus(vgid)
    total_size = int(video_down_status['totalLength'])
    down_speed = int(video_down_status['downloadSpeed'])
    completed_len = int(video_down_status['completedLength'])
    status = 'complete'
    cached = False
    if video_down_status['status'] != 'complete':
        status = 'waiting'
    if status == 'complete':
        v_md5 = get_vmd5(video_down_status['files'][0]['path'])
        if is_cached(v_md5): cached = True
    return {
        'total_size': total_size,
        'down_speed': down_speed,
        'bytes': completed_len,
        'status': status,
        'vgid': vgid,
        'agid': '',
        'cached': cached,
    }


form = cgi.FieldStorage()
action = form.getvalue('action')
s = client.ServerProxy("http://localhost:6800/rpc")
print("Content-type:application/json; charset=utf-8\r\n")

if action == 'GET':
    url = form.getvalue('url').strip()
    req = urllib.request.Request(url)
    req.add_header('Referer', 'https://www.bilibili.com/')
    req.add_header('User-Agent', USER_AGENT)
    resp = None
    try:
        resp = urllib.request.urlopen(req, timeout = 10)
    except urllib.error.HTTPError  as e:
        response_err(f"请求错误，代码：{e.code}")
    data = p_gzip_data(resp)
    m = re.search("\"title\":\"(.*?)\"", data)
    if not m:
        response_err('播放信息获取失败。')
    title = m.group(1)
    # latest video regex
    Play_INFO_r = re.findall("(video|audio)\":\[{\"id\":\d+,\"baseUrl\":\"(.*?)\"", data)
    if Play_INFO_r:
        video_m4s = Play_INFO_r[0][1]
        audio_m4s = Play_INFO_r[1][1]
        video_sum = hashlib.md5(video_m4s.encode()).hexdigest()
        vgid = s.aria2.addUri([video_m4s], { "dir": cache_root + '/video', 'out': video_sum + '.video' })
        agid = s.aria2.addUri([audio_m4s], { "dir": cache_root + '/audio', 'out': video_sum + '.audio' })
        add_Download_job(f'{vgid}:{agid}')
        video_base = { 'title': title, 'vgid': vgid, 'agid': agid, 'type': 'latest', 'v_md5': video_sum }
        video_base.update(task_status(vgid, agid))
        respone(data = video_base)
    # old video regex
    Play_INFO_r = re.search("\"url\":\"(.*?)\"", data)
    if Play_INFO_r:
        flv_video_urlfile = Play_INFO_r.group(1)
        video_sum = hashlib.md5(flv_video_urlfile.encode()).hexdigest()
        vgid = s.aria2.addUri([flv_video_urlfile], { "dir": cache_root + '/video', 'out': video_sum + '.video' })
        add_Download_job(f'{vgid}')
        video_base = { 'title': title, 'vgid': vgid, 'type': 'old', 'v_md5': video_sum }
        video_base.update(flv_task_status(vgid))
        respone(data = video_base)
    else:
        response_err('视频文件获取失败。')

elif action == 'progress':
    list = form.getvalue('list')
    video_list_json = json.loads(list)
    resp_list = []
    for task in video_list_json:
        v_data = video_list_json[task]
        vgid = v_data['data']['vgid']
        type = v_data['data']['type']
        v_md5 = v_data['data']['v_md5']
        if type == 'latest':
            # latest video
            agid = video_list_json[task]['data']['agid']
            resp_list.append({ 'task_id': v_data['task_id'], 'detail': task_status(vgid, agid) })
        elif type == 'old':
            # old video
            resp_list.append({ 'task_id': v_data['task_id'], 'detail': flv_task_status(vgid) })
    respone(data = resp_list)
