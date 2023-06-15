import os
import shutil

def conditional_download(download_directory_path: str, urls: list) -> None:
    from urllib.request import urlopen, urlretrieve
    from tqdm import tqdm
    if not os.path.exists(download_directory_path):
        os.makedirs(download_directory_path)
    for url in urls:
        download_file_path = os.path.join(download_directory_path, os.path.basename(url))
        if not os.path.exists(download_file_path):
            request = urlopen(url)
            total = int(request.headers.get('Content-Length', 0))
            with tqdm(total=total, desc='Downloading', unit='B', unit_scale=True, unit_divisor=1024) as progress:
                urlretrieve(url, download_file_path, reporthook=lambda count, block_size, total_size: progress.update(block_size))

def path(string):
    if os.name == "nt":
        return string.replace("/", os.sep)
    return string


def run_command(command, mode="silent"):
    if mode == "debug":
        return os.system(command)
    return os.popen(command).read()


def detect_fps(input_path):
    input_path = path(input_path)
    output = os.popen(f'ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate "{input_path}"').read()
    if "/" in output:
        try:
            return int(output.split("/")[0]) // int(output.split("/")[1].strip()), output.strip()
        except:
            pass
    return 30, 30


def set_fps(input_path, output_path, fps):
    input_path, output_path = path(input_path), path(output_path)
    os.system(f'ffmpeg -i "{input_path}" -filter:v fps=fps={fps} "{output_path}"')


def create_video(video_name, fps, output_dir):
    output_dir = path(output_dir)
    os.system(f'ffmpeg -framerate "{fps}" -i "{output_dir}{os.sep}%04d.png" -c:v libx264 -crf 7 -pix_fmt yuv420p -y "{output_dir}{os.sep}output.mp4"')


def extract_frames(input_path, output_dir):
    input_path, output_dir = path(input_path), path(output_dir)
    os.system(f'ffmpeg -i "{input_path}" "{output_dir}{os.sep}%04d.png"')


def add_audio(output_dir, target_path, video, keep_frames, output_file, gpu):
    video_name = os.path.splitext(video)[0]
    save_to = output_file if output_file else output_dir + "/swapped-" + video_name + ".mp4"
    save_to_ff, output_dir_ff, target_path_ff = path(save_to), path(output_dir), path(target_path)
    os.system(f'ffmpeg -i "{output_dir_ff}{os.sep}output.mp4" -i "{target_path_ff}" -c:v copy -map 0:v:0 -map 1:a:0 -y "{save_to_ff}"')
    if not os.path.isfile(save_to):
        shutil.move(output_dir + "/output.mp4", save_to)
    if not keep_frames:
        shutil.rmtree(output_dir)


def is_img(path):
    return path.lower().endswith(("png", "jpg", "jpeg", "bmp"))


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)
