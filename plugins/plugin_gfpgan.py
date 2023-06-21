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

        "default_options": {
            "upscale_gfpgan": 1,  # upscale made by gfpgan
            "upscale_final": 1, # final upscale. if different with gfpgan - will INTER_CUBIC scaled to this
        },

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
        options = self.core.plugin_options(modname)
        #pass
        model_path = './models/GFPGANv1.3.pth'
        self.face_enchancer = gfpgan.GFPGANer(
            model_path=model_path,
            channel_multiplier=2,
            upscale=options.get("upscale_gfpgan")
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

        if params.get("yes_face") is None: # we don't know is there face or not
            from roop.analyser import get_face_single

            face = get_face_single(frame)
            if face:
                params["yes_face"] = True
            else:
                params["yes_face"] = False

        options = self.core.plugin_options(modname)

        import cv2

        if params.get("yes_face") == False:
            if options.get("upscale_final") == 1:
                return frame # no scale, no face, no process
            else:
                resize_param = options.get("upscale_final")
                frame = cv2.resize(frame, None, fx=resize_param, fy=resize_param, interpolation=cv2.INTER_CUBIC)
                return frame

        # there are face!!

        frame = self.enhance_face(frame)
        if options.get("upscale_gfpgan") != options.get("upscale_final"):
            resize_param = float(options.get("upscale_final")) / float(options.get("upscale_gfpgan"))
            frame = cv2.resize(frame, None, fx=resize_param, fy=resize_param, interpolation=cv2.INTER_CUBIC)

        return frame



