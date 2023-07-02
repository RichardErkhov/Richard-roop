# Gfpgan enchance plugin
# a lot of code from original roop, next branch
# based on paulisongs#7779 code

import time
from typing import Any
from chain_img_processor import ChainImgProcessor, ChainImgPlugin
import os
import threading
import roop.globals

modname = os.path.basename(__file__)[:-3] # calculating modname

# start function
def start(core:ChainImgProcessor):
    manifest = { # plugin settings
        "name": "Gfpgan face enchancer (onnx version)", # name
        "version": "1.0", # version

        "default_options": {
            "upscale_gfpgan": 1,  # upscale made by gfpgan
            "upscale_final": 1, # final upscale. if different with gfpgan - will INTER_CUBIC scaled to this
        },

        "img_processor": {
            "gfpganonnx": PluginGfpganOnnx # 1 function - init, 2 - process
        }
    }
    return manifest


def start_with_options(core:ChainImgProcessor, manifest:dict):
    pass

import os
import sys
import argparse
import cv2
import numpy as np
import timeit
import onnxruntime

class GFPGANFaceAugment:
    def __init__(self, model_path, use_gpu=False):
        self.ort_session = onnxruntime.InferenceSession(model_path,providers=roop.globals.providers)
        self.net_input_name = self.ort_session.get_inputs()[0].name
        _, self.net_input_channels, self.net_input_height, self.net_input_width = self.ort_session.get_inputs()[0].shape
        self.net_output_count = len(self.ort_session.get_outputs())
        self.face_size = 512
        self.face_template = np.array([[192, 240], [319, 240], [257, 371]]) * (self.face_size / 512.0)
        self.upscale_factor = 2
        self.affine = False

    def pre_process(self, img):
        img = cv2.resize(img, (int(img.shape[1] / 2), int(img.shape[0] / 2)))
        img = cv2.resize(img, (self.face_size, self.face_size))
        img = img / 255.0
        img = img.astype('float32')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img[:, :, 0] = (img[:, :, 0] - 0.5) / 0.5
        img[:, :, 1] = (img[:, :, 1] - 0.5) / 0.5
        img[:, :, 2] = (img[:, :, 2] - 0.5) / 0.5
        img = np.float32(img[np.newaxis, :, :, :])
        img = img.transpose(0, 3, 1, 2)
        return img

    def post_process(self, output, height, width):
        output = output.clip(-1, 1)
        output = (output + 1) / 2
        output = output.transpose(1, 2, 0)
        output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        output = (output * 255.0).round()
        if self.affine:
            inverse_affine = cv2.invertAffineTransform(self.affine_matrix)
            inverse_affine *= self.upscale_factor
            if self.upscale_factor > 1:
                extra_offset = 0.5 * self.upscale_factor
            else:
                extra_offset = 0
            inverse_affine[:, 2] += extra_offset
            inv_restored = cv2.warpAffine(output, inverse_affine, (width, height))
            mask = np.ones((self.face_size, self.face_size), dtype=np.float32)
            inv_mask = cv2.warpAffine(mask, inverse_affine, (width, height))
            inv_mask_erosion = cv2.erode(
                inv_mask, np.ones((int(2 * self.upscale_factor), int(2 * self.upscale_factor)), np.uint8))
            pasted_face = inv_mask_erosion[:, :, None] * inv_restored
            total_face_area = np.sum(inv_mask_erosion)
            # compute the fusion edge based on the area of the face
            w_edge = int(total_face_area ** 0.5) // 20
            erosion_radius = w_edge * 2
            inv_mask_center = cv2.erode(inv_mask_erosion, np.ones((erosion_radius, erosion_radius), np.uint8))
            blur_size = w_edge * 2
            inv_soft_mask = cv2.GaussianBlur(inv_mask_center, (blur_size + 1, blur_size + 1), 0)
            inv_soft_mask = inv_soft_mask[:, :, None]
            output = pasted_face
        else:
            inv_soft_mask = np.ones((height, width, 1), dtype=np.float32)
            output = cv2.resize(output, (width, height))
        return output, inv_soft_mask

    def forward(self, img):
        height, width = img.shape[0], img.shape[1]
        img = self.pre_process(img)
        t = timeit.default_timer()
        ort_inputs = {self.ort_session.get_inputs()[0].name: img}
        ort_outs = self.ort_session.run(None, ort_inputs)
        output = ort_outs[0][0]
        output, inv_soft_mask = self.post_process(output, height, width)
        #print('infer time:', timeit.default_timer() - t)
        output = output.astype(np.uint8)
        return output, inv_soft_mask

    def process_image(self, image, faces):
        #image = cv2.imread(image_path, 1)

        # height, width = image.shape[0], image.shape[1]
        # face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        #if len(faces) > 0:
        for face in faces:
            #x, y, w, h = faces[0]
            bbox = face['bbox']
            x, y, x2, y2 = map(int, bbox)
            w = x2-x
            h = y2-y


            # Expand the bounding box
            expand_ratio = 1.3  # Adjust the expansion ratio as needed
            expanded_w = int(w * expand_ratio)
            expanded_h = int(h * expand_ratio)
            x -= int((expanded_w - w) / 2)
            y -= int((expanded_h - h) / 2)
            w = expanded_w
            h = expanded_h

            # Adjust the crop size
            crop_size = int(max(w, h) * 1.2)  # Adjust the scale factor (1.2) as needed
            x -= int((crop_size - w) / 2)
            y -= int((crop_size - h) / 2)
            w = h = crop_size

            face_image = image[max(0, y):y + h, max(0, x):x + w]
            processed_face, _ = self.forward(face_image)

            #output = image.copy()
            #output[max(0, y):y + h, max(0, x):x + w] = processed_face
            image[max(0, y):y + h, max(0, x):x + w] = processed_face
            # cv2.imshow("demo",processed_face)
            # time.sleep(2.0)

            return image

        return image

face_enchancer = None


class PluginGfpganOnnx(ChainImgPlugin):
    def init_plugin(self):
        global face_enchancer
        if face_enchancer is None:

            model_path = './models/GFPGANv1.3.onnx'
            face_enchancer = GFPGANFaceAugment(
                model_path=model_path,

            )

        self.face_enchancer = face_enchancer


    def process(self, frame, params: dict):
        if params.get("yes_face") == False: return frame

        frame2 = self.face_enchancer.process_image(frame, params["faces"])

        return frame2





