# Gfpgan enchance plugin
# a lot of code from original roop, next branch

from typing import Any
from chain_img_processor import ChainImgProcessor, ChainImgPlugin
import os
import threading

modname = os.path.basename(__file__)[:-3] # calculating modname

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

class PluginGfpgan(ChainImgPlugin):
    def init_plugin(self):
        import gfpgan
        from roop.utils import conditional_download
        conditional_download("./models",
                             ['https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth'])
        #pass
        model_path = './models/GFPGANv1.3.pth'
        self.face_enchancer = gfpgan.GFPGANer(
            model_path=model_path,
            channel_multiplier=2,
            upscale=2
        )

    def enhance_face(self, temp_frame: Any) -> Any:
        #THREAD_SEMAPHORE.acquire()
        _, _, temp_frame = self.face_enchancer.enhance(
            temp_frame,
            paste_back=True
        )
        #THREAD_SEMAPHORE.release()
        return temp_frame

    def process(self, frame, params:dict):
        # params can be used to transfer some img info to next processors
        if params.get("yes_face") == False: return frame # no face, no process

        from roop.analyser import get_face_many, get_face_single
        from roop.swapper import get_face_swapper
        import cv2

        yes_face = False

        face = get_face_single(frame)
        if face:
            frame = self.enhance_face(frame) # this double image size
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
            yes_face = True

        params["yes_face"] = yes_face

        return frame



