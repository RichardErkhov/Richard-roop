# Join the discord server (this is not official roop server!) https://discord.gg/hzrJBGPpgN
Take a video and replace the face in it with a face of your choice. You only need one image of the desired face. No dataset, no training.

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


