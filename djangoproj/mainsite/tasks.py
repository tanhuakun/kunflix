from celery.task.schedules import crontab
from celery import shared_task
from mylogin.models import Invites, ForgetPassword, RegisterAttempts
import random
import string
from djangoproj.celery import app as celery_app
from django.conf import settings
from .models import Show
import os
import subprocess
from subprocess import check_output
import shlex
import re
import json
import shutil
from django.utils import timezone
from datetime import datetime
from datetime import timezone as _
import requests
from django.core import management


inputpath = settings.MYINPUT_PATH
video = settings.VIDEO_PATH
captions = settings.CAPTIONS_PATH
thumbnail = settings.THUMBNAIL_PATH
fail = settings.FAIL_PATH

@shared_task(name = 'update_ydns')
def update_ydns():
    myip = requests.get('https://api.ipify.org')

    ydns_url = removed

    myreq = requests.get(ydns_url, auth=('huakun99@gmail.com', removed))

@shared_task(name='clear_stuff')
def clear_stuff():
    management.call_command('clearsessions', verbosity=0)
    management.call_command('axes_reset_logs', '--age=15', verbosity=0)
    myreg = RegisterAttempts.objects.all()
    myforget = ForgetPassword.objects.all()
    
    for x in myreg:
        if ( (datetime.now(_.utc) - x.date).total_seconds() / (60 * 60) ) > 168:
            x.delete()
    for x in myforget:
        if ( (datetime.now(_.utc) - x.date).total_seconds() / (60 * 60) )  > 48:
            x.delete()
    

@celery_app.task(name="foobar.sample_task")
def sample_task(value):
    letters = string.ascii_letters
    p = Invites(code =  ''.join(random.choice(letters) for i in range(10)))
    p.save()

@shared_task
def routine_encode(name = 'routine_encode'):
    all_files = sorted(os.listdir(inputpath))
    failed_list = []
    all_files.remove('.stfolder')
    
    for idv_file in all_files:
        
        if idv_file[-4:] != ".mkv":
            failed_list.append(idv_file)
            continue
        
        #my variables from my file name.
        name = ''
        episode = 0
        is_movie = False
        # start pattern recognition, if anime, anime movie, normal, normal movie.
        if idv_file.count(' ') > 2:
            pattern = '(?:.*[\])] *|^)(.+) - (\d{1,3})\D'
            result = re.search(pattern, idv_file)
            if result:
                name = result.group(1)
                episode = int(result.group(2))
            else:
                pattern = '(?:.*[\])] *|^)(.*) - (\d{4})\D'
                result = re.search(pattern, idv_file)
                if result:
                    name = result.group(1) + f" ({result.group(2)})"
                    is_movie = True
                else:
                    failed_list.append(idv_file)
                    continue
        else:
            tempfile = idv_file.replace('.', ' ')
            pattern = '(.+ S\d{1,3})E(\d{1,3})'
            result = re.search(pattern, tempfile)
            if result: 
                name=result.group(1)
                episode = int(result.group(2))
            else:
                pattern = '(?:.*[\])] *|^)(.+) (\d{4}) 1080p'
                result = re.search(pattern, tempfile)
                if result:
                    name = result.group(1) + f" ({result.group(2)})"
                    is_movie = True
                else:
                    failed_list.append(idv_file)
                    print("here")
                    continue
        # look for the show, if not create one.
        name_path = name + "\\"
        try:
            show_obj = Show.objects.get(path=name)
            ## handle anime shounen continous episodes.
            if show_obj.max_episode:
                counter = 1
                while show_obj.max_episode:
                    counter += 1
                    episode -= show_obj.max_episode
                    if counter == 2:
                        name += (" S" + str("%02d" % counter))
                    else:
                        name = name[:-2]
                        name += str("%02d" % counter)
                    name_path = name + "\\"
                    show_obj = Show.objects.get(path=name)



        except Show.DoesNotExist:
            if episode <= 1: 
                show_obj = Show(title=name, episodes=0, path=name, category = 'Unknown', recentdate = timezone.now())
                for new_path in [video, captions, thumbnail]:
                    try:
                        os.makedirs(os.path.join(new_path, name_path))
                    except:
                        pass
            else:
                failed_list.append(idv_file)
                continue
        # if not movie, check against episode.
        if not is_movie:
            if show_obj.episodes + 1 != episode:
                failed_list.append(idv_file)
                continue
        
        #change episode number
        show_obj.episodes = episode
        show_obj.save()
        #start encoding
        
        sub_check = shlex.split(f"ffprobe -print_format json -show_streams -select_streams s -pretty -loglevel quiet \"{inputpath + idv_file}\"")
        aud_check = shlex.split(f"ffprobe -print_format json -show_streams -select_streams a -pretty -loglevel quiet \"{inputpath + idv_file}\"")

        p = subprocess.Popen(sub_check, stdout=subprocess.PIPE)
        p.wait()
        out, err = p.communicate()
        sub_streams = json.loads(out)
        sub_index = -1
        for stream in sub_streams['streams']:
            if stream['tags']['language'] == 'eng' and stream['disposition']['forced'] == 0:
                sub_index = stream['index']
                break

        p = subprocess.Popen(aud_check, stdout=subprocess.PIPE)
        p.wait()
        out, err = p.communicate()
        aud_streams = json.loads(out)
        aud_is_aac = False #default
        if aud_streams['streams'][0]['codec_name'] == 'aac':
            aud_is_aac = True
        

        if aud_is_aac:
            os.system(f"ffmpeg -i \"{inputpath + idv_file}\" -map 0:v:0 -map 0:a:0 -c:v copy -c:a copy -sn \"{str(video + name_path + idv_file)[:-4] + '.mp4'}\"")
        else:
            os.system(f"ffmpeg -i \"{inputpath + idv_file}\" -map 0:v:0 -map 0:a:0 -c:v copy -c:a aac -ac 2 -sn \"{str(video + name_path + idv_file)[:-4] + '.mp4'}\"")

        if sub_index is not -1:
            os.system(f"ffmpeg -i \"{inputpath + idv_file}\" -map 0:{sub_index} \"{str(captions + name_path + idv_file)[:-4] + '.vtt'}\"")
        
        os.system(f"ffmpeg -i \"{inputpath + idv_file}\" -vframes 1 -an -s 480x270 -ss 10 \"{str(thumbnail + name_path + idv_file)[:-4] + '.jpg'}\"")
        

    for to_move in failed_list:
        shutil.copy(inputpath + to_move, fail)
    for to_delete in all_files:
        os.remove(inputpath + to_delete)


'''
potentially reset axes
remember to clearsessions()
'''