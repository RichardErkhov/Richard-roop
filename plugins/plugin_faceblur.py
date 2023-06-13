# Faceblur

from chain_img_processor import ChainImgProcessor, ChainImgPlugin
import os

modname = os.path.basename(__file__)[:-3] # calculating modname

# start function
def start(core:ChainImgProcessor):
    manifest = { # plugin settings
        "name": "Faceblur", # name
        "version": "1.0", # version

        "img_processor": {
            "faceblur": Faceblur # 1 function - init, 2 - process
        }
    }
    return manifest

def proc_blur(img,face):
    import cv2
    bbox = face['bbox']

    x1, y1, x2, y2 = map(int, bbox)

    # Get region of interest
    roi = img[y1:y2, x1:x2]

    # Apply blur to region of interest
    blur = cv2.blur(roi, (30, 30))

    # Replace region of interest with blurred region
    img[y1:y2, x1:x2] = blur

    return img


class Faceblur(ChainImgPlugin):

    def process(self, frame, params:dict):
        # params can be used to transfer some img info to next processors
        if params.get("yes_face") == False: return frame # no face, no process

        from roop.analyser import get_face_many, get_face_single
        from roop.swapper import get_face_swapper

        all_faces = params.get("all_faces")
        swap = get_face_swapper()

        yes_face = False
        if all_faces:
            many_faces = get_face_many(frame)
            if many_faces:
                for face in many_faces:
                    #frame = swap.get(frame, face, params.get("source_face"), paste_back=True)
                    frame = proc_blur(frame, face)

                yes_face = True
        else:
            face = get_face_single(frame)
            if face:
                #frame = swap.get(frame, face, params.get("source_face"), paste_back=True)
                frame = proc_blur(frame, face)
                yes_face = True

        params["yes_face"] = yes_face

        return frame
