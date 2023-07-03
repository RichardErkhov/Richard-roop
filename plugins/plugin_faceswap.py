# Faceswap

from chain_img_processor import ChainImgProcessor, ChainImgPlugin
import os

modname = os.path.basename(__file__)[:-3] # calculating modname

# start function
def start(core:ChainImgProcessor):
    manifest = { # plugin settings
        "name": "Faceswap", # name
        "version": "1.0", # version

        "img_processor": {
            "faceswap": Faceswap # 1 function - init, 2 - process
        }
    }
    return manifest


class Faceswap(ChainImgPlugin):

    def process(self, frame, params:dict):
        # params can be used to transfer some img info to next processors
        if params.get("yes_face") == False: return frame # no face, no process

        if params.get("yes_face") is None: raise ValueError("Please, add 'facedetect' in chain before 'faceswap' to detect faces")

        from roop.swapper import get_face_swapper

        swap = get_face_swapper()

        many_faces = params.get("faces")

        for face in many_faces:
            frame = swap.get(frame, face, params.get("source_face"), paste_back=True)

        return frame
