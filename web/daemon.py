import os
import pathlib
import socket
import subprocess
import sys
import threading
import time
from xmlrpc import client

import daemon

cached_list = { }
converted_list = []
jobs = []

work_dir = pathlib.Path(__file__).parent.absolute()
os.chdir(work_dir)
s = client.ServerProxy("http://localhost:6800/rpc")


def m4s_to_mp4(name):
    out = f'download/{name}.mp4'
    video_m4s_dir = 'caches/video/'
    audio_m4s_dir = 'caches/audio/'
    video = video_m4s_dir + name + '.video'
    audio = audio_m4s_dir + name + '.audio'
    if not os.path.exists(video) or not os.path.exists(audio): return
    if os.path.exists(out):
        print(f'{out} video has exist!')
        return
    proc = subprocess.Popen(['ffmpeg', '-i', video, '-i', audio, '-c', 'copy', out], shell = False)
    try:
        outs, errs = proc.communicate(timeout = 60 * 3)
        try:
            converted_list.append(name)
            os.unlink(video)
            os.unlink(audio)
        except:
            pass
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

def flv_to_mp4(name):
    out = f'download/{name}.mp4'
    video_dir = 'caches/video/'
    video_file = video_dir + name + '.video'
    if not os.path.exists(video_file) : return
    if os.path.exists(out):
        print(f'{out} video has exist!')
        return
    proc = subprocess.Popen(['ffmpeg', '-i', video_file, '-c', 'copy', out], shell = False)
    try:
        outs, errs = proc.communicate(timeout = 60 * 3)
        try:
            converted_list.append(name)
            os.unlink(video_file)
        except:
            pass
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

def is_convertd(v_md5):
    if v_md5 in converted_list:
        return True

def rev_jobs():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', 7000))
        sock.listen()
    except:
        exit()
    while True:
        connection, client_address = sock.accept()
        try:
            data = connection.recv(64)
            print('received {!r}'.format(data))
            if b'is_convertd:' in data:
                s = data.decode().split(':')
                if is_convertd(s[1]):
                    connection.send(b'ok')
                else:
                    connection.send(b'no')
                continue
            gid = data
            if gid:
                if not gid in jobs: jobs.append(gid)
        finally:
            connection.close()

def m4s_video_convert(g):
    gid_group = g.decode().split(':')
    video_gid, audio_gid = gid_group[0], gid_group[1]
    v_status = s.aria2.tellStatus(video_gid)
    a_status = s.aria2.tellStatus(audio_gid)
    if v_status['status'] != 'complete': return
    if a_status['status'] != 'complete': return
    jobs.remove(g)
    path = v_status['files'][0]['path']
    if not os.path.exists(path): return
    name = os.path.splitext(os.path.basename(path))[0]
    thr = threading.Thread(target = m4s_to_mp4, args = (name,))
    thr.start()

def flv_video_convert(g):
    gid = g.decode()
    v_status = s.aria2.tellStatus(gid)
    if v_status['status'] != 'complete': return
    jobs.remove(g)
    path = v_status['files'][0]['path']
    if not os.path.exists(path): return
    name = os.path.splitext(os.path.basename(path))[0]
    thr = threading.Thread(target = flv_to_mp4, args = (name,))
    thr.start()

def runner():
    watch_thr = threading.Thread(target = rev_jobs)
    watch_thr.start()
    while True:
        for g in jobs:
            if ':' in g.decode():
                # latest video process
                m4s_video_convert(g)
            else:
                # old video progress
                flv_video_convert(g)
        time.sleep(1)

if __name__ == "__main__":
    os.system('mkdir -p caches/video caches/audio')
    sys.argv.append(None)
    if sys.argv[1] == '-d':
        with daemon.DaemonContext():
            runner()
    else:
        runner()
