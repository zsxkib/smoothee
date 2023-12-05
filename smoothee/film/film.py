from concurrent.futures import ThreadPoolExecutor
import os
import glob
import time
import shutil
import subprocess
import tensorflow as tf
from typing import NoReturn

from pathlib import Path
from .eval import interpolator as film_interpolator, util as film_util


downloads = [
    (
        "https://storage.googleapis.com/replicate-weights/film/frame_interpolation_saved_model/keras_metadata.pb",
        "smoothee/film/frame_interpolation_saved_model/keras_metadata.pb",
    ),
    (
        "https://storage.googleapis.com/replicate-weights/film/frame_interpolation_saved_model/saved_model.pb",
        "smoothee/film/frame_interpolation_saved_model/saved_model.pb",
    ),
    (
        "https://storage.googleapis.com/replicate-weights/film/frame_interpolation_saved_model/variables/variables.data-00000-of-00001",
        "smoothee/film/frame_interpolation_saved_model/variables/variables.data-00000-of-00001",
    ),
    (
        "https://storage.googleapis.com/replicate-weights/film/frame_interpolation_saved_model/variables/variables.index",
        "smoothee/film/frame_interpolation_saved_model/variables/variables.index",
    ),
]


def download_weights(url: str, dest: str) -> NoReturn:
    # Convert dest to a Path object
    dest = Path(dest)

    # Check if the destination directory exists, if not, create it
    dest_dir = dest.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Check if the destination file already exists
    if not dest.exists():
        start = time.time()
        print("[!] Starting download from URL: ", url)
        print("[!] Destination for download: ", dest)

        # Check if pget is available
        if shutil.which("pget"):
            try:
                subprocess.check_call(["pget", url, str(dest)], close_fds=False)
            except subprocess.CalledProcessError:
                print("[!] pget failed, falling back to wget")
                subprocess.check_call(["wget", url, "-O", str(dest)], close_fds=False)
        else:
            subprocess.check_call(["wget", url, "-O", str(dest)], close_fds=False)

        print("[!] Download completed. Time taken: ", time.time() - start)
    else:
        print(f"[!] File already exists at destination: {dest}. No download needed.")


class Film:
    def __init__(self):
        # Running the downloads in parallel
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(download_weights, url, dest) for url, dest in downloads
            ]

        # Ensure all downloads are complete before proceeding
        for future in futures:
            future.result()

        print("[!] Loading interpolator...")
        gpus = tf.config.experimental.list_physical_devices("GPU")
        if gpus:
            try:
                # Currently, memory growth needs to be the same across GPUs
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logical_gpus = tf.config.experimental.list_logical_devices("GPU")
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
            except RuntimeError as e:
                # Memory growth must be set before GPUs have been initialized
                print(e)

        self.interpolator = film_interpolator.Interpolator(
            "smoothee/film/frame_interpolation_saved_model",
            None,
        )

    def interp(
        self,
        input_mp4_path: Path,  # Provide an input_mp4_path video file for frame interpolation.
        playback_frames_per_second: int = 24,  # Specify the playback speed in frames per second.
        num_interpolation_steps: int = 1,  # Number of steps to interpolate between animation frames
        output_mp4_path: Path = None,  # Optional output file path
    ) -> Path:
        # If output_mp4_path is not provided, create a new file in the same location as the input file with the prefix "smoothee"
        if output_mp4_path is None:
            output_mp4_path = input_mp4_path.parent / f"smoothee_{input_mp4_path.name}"
        output_video = str(output_mp4_path)

        output_dir = Path("frames")
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        else:
            shutil.rmtree(str(output_dir))
            output_dir.mkdir(parents=True)
        output_pattern = output_dir / "%04d.png"

        try:
            subprocess.run(
                ["ffmpeg", "-i", str(input_mp4_path), str(output_pattern)],
                check=True,
            )
        except Exception as e:
            print(f"[!] Error running ffmpeg: {e}")
            return None

        original_frame_filenames = sorted(glob.glob(str(output_dir / "*.png")))

        print("[!] Interpolating frames with FILM...")
        interpolated_frames = film_util.interpolate_recursively_from_files(
            original_frame_filenames, num_interpolation_steps, self.interpolator
        )
        interpolated_frames = list(interpolated_frames)

        interpolated_frames_dir = output_dir / "interpolated_frames"
        if interpolated_frames_dir.exists():
            shutil.rmtree(str(interpolated_frames_dir))
        interpolated_frames_dir.mkdir(parents=True)

        for i, frame in enumerate(interpolated_frames):
            frame_filename = interpolated_frames_dir / f"{i:08d}.png"
            film_util.write_image(str(frame_filename), frame)

        input_pattern = interpolated_frames_dir / "%08d.png"
        output_video = str(output_mp4_path)

        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-r",
            str(playback_frames_per_second),
            "-i",
            str(input_pattern),
            "-vcodec",
            "libx264",
            "-crf",
            "1",
            "-pix_fmt",
            "yuv420p",
            output_video,
        ]

        try:
            subprocess.run(ffmpeg_command, check=True)
        except Exception as e:
            print(f"[!] Error running ffmpeg: {e}")
            return None

        print(f"[!] Output video saved at: {output_video}")
        return Path(output_video)
