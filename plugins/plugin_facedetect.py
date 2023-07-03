# Facedetect

from chain_img_processor import ChainImgProcessor, ChainImgPlugin
import os

modname = os.path.basename(__file__)[:-3] # calculating modname

# start function
def start(core:ChainImgProcessor):
    manifest = { # plugin settings
        "name": "Facedetect", # name
        "version": "1.0", # version

        "img_processor": {
            "facedetect": Facedetect # 1 function - init, 2 - process
        }
    }
    return manifest


class Facedetect(ChainImgPlugin):

    def process(self, frame, params:dict):
        # this will detect faces on scene
        if params.get("yes_face") is None:

            from roop.analyser import get_face_many, get_face_single

            all_faces = params.get("all_faces")

            yes_face = False
            if all_faces or all_faces is None:
                many_faces = get_face_many(frame)
                if many_faces:
                    yes_face = True
                    params["faces"] = many_faces
            else:
                face = get_face_single(frame)
                if face:
                    yes_face = True
                    params["faces"] = [face]

            params["yes_face"] = yes_face

        return frame
