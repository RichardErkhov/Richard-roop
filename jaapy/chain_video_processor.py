from threading import Thread
from jaapy.chain_img_processor import ChainImgProcessor
from termcolor import colored, cprint
from typing import Any
import cv2
from tqdm import tqdm
from jaapy.ffmpeg_writer import FFMPEG_VideoWriter # ffmpeg install needed

class ThreadWithReturnValue(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


# in beta
class ChainVideoProcessor(ChainImgProcessor):
    def __init__(self):
        ChainImgProcessor.__init__(self)

    def run_video_chain(self, source_video, target_video, fps, threads:int = 1, chain = None, params_frame_gen_func = None, video_codec = "libx265", video_crf = 14, video_audio = None):

        cap = cv2.VideoCapture(source_video)
        # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # first frame do manually - because upscale may happen, we need to estimate width/height
        ret, frame = cap.read()
        if params_frame_gen_func is not None:
            params = params_frame_gen_func(self, frame)
        else:
            params = {}
        frame_processed, params = self.run_chain(frame,params,chain)
        height, width, channels = frame_processed.shape

        self.fill_processors_for_thread_chains(threads,chain)
        #print(self.processors_objects)
        #import threading
        #locks:list[threading.Lock] = []
        locks: list[bool] = []
        for i in range(threads):
            #locks.append(threading.Lock())
            locks.append(False)

        temp = []
        with FFMPEG_VideoWriter(target_video, (width, height), fps, codec=video_codec, crf=video_crf, audiofile=video_audio) as output_video_ff:
            with tqdm(total=frame_count, desc='Processing', unit="frame", dynamic_ncols=True,
                      bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]') as progress:

                # do first frame
                output_video_ff.write_frame(frame_processed)
                progress.update(1) #
                cnt_frames = 0

                # do rest frames
                while True:
                    # getting frame
                    ret, frame = cap.read()

                    if not ret:
                        break
                    cnt_frames+=1
                    thread_ind = cnt_frames % threads
                    # we are having an array of length %gpu_threads%, running in parallel
                    # so if array is equal or longer than gpu threads, waiting
                    #while len(temp) >= threads:
                    while locks[thread_ind]:
                        #print('WAIT', thread_ind)
                        # we are order dependent, so we are forced to wait for first element to finish. When finished removing thread from the list
                        frame_processed, params = temp.pop(0).join()
                        locks[params["_thread_index"]] = False
                        #print('OFF',cnt_frames,locks[params["_thread_index"]],locks)
                        # writing into output
                        output_video_ff.write_frame(frame_processed)
                        # updating the status
                        progress.update(1)

                    # calc params for frame
                    if params_frame_gen_func is not None:
                        params = params_frame_gen_func(self,frame)
                    else:
                        params = {}

                    # adding new frame to the list and starting it
                    locks[thread_ind] = True
                    #print('ON', cnt_frames, thread_ind, locks)
                    temp.append(
                        ThreadWithReturnValue(target=self.run_chain, args=(frame, params, chain, thread_ind)))
                    temp[-1].start()

                while len(temp) > 0:
                    # we are order dependent, so we are forced to wait for first element to finish. When finished removing thread from the list
                    frame_processed, params = temp.pop(0).join()
                    locks[params["_thread_index"]] = False
                    # writing into output
                    output_video_ff.write_frame(frame_processed)

                    progress.update(1)

                #print("FINAL", locks)

    def run_video_chain_single_processor(self, source_video, target_video, fps, threads:int = 1, chain = None, params_frame_gen_func = None, video_codec = "libx265", video_crf = 14, video_audio = None):

        cap = cv2.VideoCapture(source_video)
        # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # first frame do manually - because upscale may happen, we need to estimate width/height
        ret, frame = cap.read()
        if params_frame_gen_func is not None:
            params = params_frame_gen_func(self, frame)
        else:
            params = {}
        frame_processed, params = self.run_chain(frame,params,chain)
        height, width, channels = frame_processed.shape


        temp = []
        with FFMPEG_VideoWriter(target_video, (width, height), fps, codec=video_codec, crf=video_crf, audiofile=video_audio) as output_video_ff:
            with tqdm(total=frame_count, desc='Processing', unit="frame", dynamic_ncols=True,
                      bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]') as progress:

                # do first frame
                output_video_ff.write_frame(frame_processed)
                progress.update(1) #

                # do rest frames
                while True:
                    # getting frame
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # we are having an array of length %gpu_threads%, running in parallel
                    # so if array is equal or longer than gpu threads, waiting
                    while len(temp) >= threads:
                        # we are order dependent, so we are forced to wait for first element to finish. When finished removing thread from the list
                        frame_processed, params = temp.pop(0).join()
                        # writing into output
                        output_video_ff.write_frame(frame_processed)
                        # updating the status
                        progress.update(1)

                    # calc params for frame
                    if params_frame_gen_func is not None:
                        params = params_frame_gen_func(self,frame)
                    else:
                        params = {}

                    # adding new frame to the list and starting it
                    temp.append(
                        ThreadWithReturnValue(target=self.run_chain, args=(frame, params, chain)))
                    temp[-1].start()

                while len(temp) > 0:
                    # we are order dependent, so we are forced to wait for first element to finish. When finished removing thread from the list
                    frame_processed, params = temp.pop(0).join()
                    # writing into output
                    output_video_ff.write_frame(frame_processed)

                    progress.update(1)

_video_processor:ChainVideoProcessor = None
def get_single_video_processor() -> ChainVideoProcessor:
    global _video_processor
    if _video_processor is None:
        _video_processor = ChainVideoProcessor()
        _video_processor.init_with_plugins()
    return _video_processor
