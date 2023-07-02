# Join the discord server (this is not official roop server!) https://discord.gg/hzrJBGPpgN
Take a video and replace the face in it with a face of your choice. You only need one image of the desired face. No dataset, no training.

Also allow row render (original, faceswap, enchance face via codeformer or gfpgan):

![demo-gif](demo_faceswap_codeformer.jpg)


# easy installation guide for windows users
```
1) install visual studio 2022 with desktop development C++ and python development (not sure about python development)
2) install python 3.10.x (any 3.10)
3) download the last version of roop
4) pip install virtualenv
5) virtualenv venv
6) start venv\scripts\activate.bat
7) pip install -r requirements.txt
that's for cpu (sometimes works for gpu for some reason)
if you want nvidia gpu to work:
don't go for cpu
1) install visual studio 2022 with desktop development C++ and python development (not sure about python development)
2) install cuda 11.7 (https://developer.nvidia.com/cuda-11-7-0-download-archive)
3) download cudnn 8.9.1 for cuda 11.x https://developer.nvidia.com/rdp/cudnn-archive
4) unpack cudnn over C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.7 with replacement
5) install python 3.10.x (any 3.10)
6) download the last version of roop
7) pip install virtualenv
8) virtualenv venv
9) start venv\scripts\activate.bat
10) pip install torch torchvision torchaudio --force-reinstall --index-url https://download.pytorch.org/whl/cu117
11) pip install -r requirements.txt
and yes, don't forget to download ffmpeg https://ffmpeg.org/download.html
and inswrapper_128.onnx https://drive.google.com/file/d/1eu60OrRtn4WhKrzM4mQv4F3rIuyUXqfl/view?usp=drive_link
```

# usage example 
```
#usage is simple:
python run.py --gpu --gpu-threads %number_of_threads%
```
for number of threads I recommend to play, for nice approximation of first step is:
amount of threads = (GPU VRAM - 1)/800

![demo-gif](demo.gif)

# Face enchancement

You can also apply face enchancement by codeformer or gfpgan (slow!!)

## For gfpgan (slightly faster then codeformer)

To do:
- In options/core.json change "default_chain": "faceswap,gfpgan"

Or if you want just enhance your video:
- In options/core.json change "default_chain": "codeformer"

## For codeformer

To do:
- Download plugin here: https://github.com/janvarev/chain-img-plugin-codeformer
- Copy it to plugins folder
- Install requirements.txt
- In options/core.json change "default_chain": "faceswap,codeformer"

Or if you want just enhance your video:
- In options/core.json change "default_chain": "codeformer"

It's recommended to set settings in options/codeformer.json like:
```json
{
    "background_enhance": false,
    "codeformer_fidelity": 0.5,
    "face_upsample": true,
    "skip_if_no_face": true,
    "upscale": 1
}
```

### For gfpganonnx

Effective implementation of GFPGAN on ONNX (I gain 2.5x speedup)

To use: 
- convert GFPGAN model to ONNX format https://github.com/xuanandsix/GFPGAN-onnxruntime-demo/tree/main
- your resulted model must be placed as `./models/GFPGANv1.3.onnx`
- In options/core.json change "default_chain": "faceswap,gfpganonnx"
- Note: If you wanna just ehchance face on current video, use "default_chain": "gfpganonnx"


# Special thanks

https://github.com/janvarev/chain-img-processor licensed under MIT


