# Gfpgan enchance plugin
# a lot of code from original roop, next branch

import urllib
from typing import List, Any

from tqdm import tqdm

from chain_img_processor import ChainImgProcessor, ChainImgPlugin
import os
import threading

modname = os.path.basename(__file__)[:-3] # calculating modname

FACE_ENHANCER = None
THREAD_SEMAPHORE = threading.Semaphore()
THREAD_LOCK = threading.Lock()

# start function
def start(core:ChainImgProcessor):
    manifest = { # plugin settings
        "name": "Gfpgan face enchancer", # name
        "version": "1.0", # version

        "img_processor": {
            "gfpgan": PluginGfpgan # 1 function - init, 2 - process
        }
    }
    return manifest

def start_with_options(core:ChainImgProcessor, manifest:dict):
    pass

def conditional_download(download_directory_path: str, urls: List[str]) -> None:
    if not os.path.exists(download_directory_path):
        os.makedirs(download_directory_path)
    for url in urls:
        download_file_path = os.path.join(download_directory_path, os.path.basename(url))
        if not os.path.exists(download_file_path):
            request = urllib.request.urlopen(url)
            total = int(request.headers.get('Content-Length', 0))
            with tqdm(total=total, desc='Downloading', unit='B', unit_scale=True, unit_divisor=1024) as progress:
                urllib.request.urlretrieve(url, download_file_path, reporthook=lambda count, block_size, total_size: progress.update(block_size))

def get_face_enhancer() -> None:
    import gfpgan
    global FACE_ENHANCER

    with THREAD_LOCK:
        if FACE_ENHANCER is None:
            model_path = './models/GFPGANv1.3.pth'
            FACE_ENHANCER = gfpgan.GFPGANer(
                model_path=model_path,
                channel_multiplier=2,
                upscale=2
            )
    return FACE_ENHANCER

def enhance_face(temp_frame: Any) -> Any:
    THREAD_SEMAPHORE.acquire()
    _, _, temp_frame = get_face_enhancer().enhance(
        temp_frame,
        paste_back=True
    )
    THREAD_SEMAPHORE.release()
    return temp_frame

class PluginGfpgan(ChainImgPlugin):
    def init_plugin(self):
        import gfpgan
        conditional_download("./models",
                             ['https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth'])
        #pass

    def process(self, frame, params:dict):
        # params can be used to transfer some img info to next processors
        if params.get("yes_face") == False: return frame # no face, no process

        from roop.analyser import get_face_many, get_face_single
        from roop.swapper import get_face_swapper
        import cv2

        yes_face = False

        face = get_face_single(frame)
        if face:
            frame = enhance_face(frame)
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
            yes_face = True

        params["yes_face"] = yes_face

        return frame



