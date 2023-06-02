from roop.swapper import get_face_swapper
from roop.analyser import get_face_analyser
from roop.utils import open_video, open_video_writer
import cv2
from tqdm import tqdm
import os
from roop.analyser import get_face_single, get_face_many
from roop.thread_handling import create_thread, get_result_from_thread
import roop.globals
import time

def face_analyser_thread(frame, source_face, all_faces):
    has_face = False
    if all_faces:
        many_faces = get_face_many(frame)
        if many_faces:
            for face in many_faces:
                frame = swap.get(frame, face, source_face, paste_back=True)
            has_face = True
    else:
        face = get_face_single(frame)
        if face:
            frame = swap.get(frame, face, source_face, paste_back=True)
            has_face = True   
    return has_face, frame
def process_video_gpu(source_img, source_video, out, fps, gpu_threads, all_faces):
    global face_analyser, swap
    swap = get_face_swapper()
    face_analyser = get_face_analyser()
    source_face = get_face_single(cv2.imread(source_img))
    video = open_video(source_video)
    output_video = open_video_writer(video, out, fps)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    temp = []
    counter = 0
    with tqdm(total=frame_count, desc='Processing', unit="frame", dynamic_ncols=True, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]') as progress:
        while True:
            ret, frame = video.read()
            if not ret:
                break

            while len(temp) >= gpu_threads:
                waiting_for = temp[0][0]
                result_found = False
                while result_found == False:
                    for number, thread in enumerate(roop.globals.results):
                        if thread[0] == waiting_for:
                            result_found = True
                            break
                result = roop.globals.results.pop(number)[1]
                temp.pop(0)
                has_face, x = result
                #has_face, x = get_result_from_thread(first_thread)
                output_video.write(x)
                if has_face:
                    progress.set_postfix(status='.', refresh=True)
                else:
                    progress.set_postfix(status='S', refresh=True)
                progress.update(1)
                counter += 1
            a = create_thread(face_analyser_thread, counter, (frame,  source_face, all_faces))
            a.start()
            temp.append([counter, a])

def process_video_gpus(source_img, source_video, out, fps, gpu_threads, all_faces):
    global face_analyser, swap
    swap = get_face_swapper()
    face_analyser = get_face_analyser()
    source_face = get_face_single(cv2.imread(source_img))
    video = open_video(source_video)
    output_video = open_video_writer(video, out, fps)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    temp = []
    counter = 0
    with tqdm(total=frame_count, desc='Processing', unit="frame", dynamic_ncols=True, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]') as progress:
        while True:
            ret, frame = video.read()
            if not ret:
                break
            while len(temp) >= gpu_threads:
                #first_thread = temp.pop(0)
                result_found = False
                while result_found == False:
                    for number, thread in enumerate(roop.globals.results):
                        if thread[0] == counter:
                            result_found = True
                    time.sleep(0.001)
                result = roop.globals.results.pop(number)[1]
                temp.pop(0)
                has_face, x = result
                #has_face, x = get_result_from_thread(first_thread)
                output_video.write(x)
                if has_face:
                    progress.set_postfix(status='.', refresh=True)
                else:
                    progress.set_postfix(status='S', refresh=True)
                progress.update(1)
                counter += 1
            a = create_thread(face_analyser_thread, counter, (frame,  source_face, all_faces))
            a.start()
            temp.append([counter, a])
