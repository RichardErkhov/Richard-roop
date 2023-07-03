# Faceswap selective

from chain_img_processor import ChainImgProcessor, ChainImgPlugin
import os

modname = os.path.basename(__file__)[:-3] # calculating modname

# start function
def start(core:ChainImgProcessor):
    manifest = { # plugin settings
        "name": "Faceswap selective", # name
        "version": "1.0", # version

        "default_options": {
            "selective": "",  # "char1.jpg->new1.jpg||char2.jpg->new2.jpg" etc.
            "max_distance": 0.85, # max distance to detect face similarity
        },

        "img_processor": {
            "faceswap_selective": FaceswapSelective # 1 function - init, 2 - process
        }
    }
    return manifest

def start_with_options(core:ChainImgProcessor, manifest:dict):
    pass

face_list:list = None

import cv2

class FaceswapSelective(ChainImgPlugin):

    def init_plugin(self):
        global face_list
        if face_list is None:
            from roop.analyser import get_face_many

            face_list = []
            options = self.core.plugin_options(modname)
            selective = str(options["selective"])

            sel_ar = selective.split("||")
            for el in sel_ar:
                ffrom, fto = el.split("->")

                img_from = cv2.imread(ffrom)
                faces = get_face_many(img_from)
                if len(faces) > 1: raise ValueError(f"There must be only 1 face on {ffrom} image")
                if len(faces) == 0: raise ValueError(f"No face detected on {ffrom} image")
                face_from = faces[0]

                img_to = cv2.imread(fto)
                faces = get_face_many(img_to)
                if len(faces) > 1: raise ValueError(f"There must be only 1 face on {fto} image")
                if len(faces) == 0: raise ValueError(f"No face detected on {fto} image")
                face_to = faces[0]

                face_list.append([face_from,img_from,face_to,img_to])

    def distance_near(self, face, reference_face):
        import numpy
        distance = numpy.sum(numpy.square(face.normed_embedding - reference_face.normed_embedding))
        #print(distance)
        if distance < self.core.plugin_options(modname).get("max_distance"):
            #print("face passed")
            return True
        return False

    def process(self, frame, params:dict):
        # params can be used to transfer some img info to next processors
        if params.get("yes_face") is None: raise ValueError("Please, add 'facedetect' in chain before 'faceswap_selective' to detect faces")

        if params.get("yes_face") == False: return frame # no face, no process

        from roop.swapper import get_face_swapper

        swap = get_face_swapper()

        many_faces = params.get("faces")

        for face in many_faces:
            for reference in face_list:
                reference_face, _, target_face, _ = reference
                if self.distance_near(face, reference_face):
                    frame = swap.get(frame, face, target_face, paste_back=True)

        return frame
