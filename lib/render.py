from typing import List
import ffmpeg

from lib.log import time_log


def combine_videos(input_files: List[str], output_file: str):
    """
    複数の動画ファイルを結合する。
    """
    inputs = [ffmpeg.input(file) for file in input_files]
    combined = ffmpeg.concat(*inputs)
    with time_log("combine_videos"):
        ffmpeg.output(combined, output_file).run(overwrite_output=True, quiet=True)


def render_zoomed_video(
    input_file: str, output_file: str, zoom_factor: float = 0.9, center: bool = True
):
    """
    動画の中央にズームしたバージョンをレンダリングする。
    zoom_factor: ズームする割合 (0.0 ~ 1.0)
    center: True の場合、中央にズームする
    """
    probe = ffmpeg.probe(input_file)
    video_info = next(
        stream for stream in probe["streams"] if stream["codec_type"] == "video"
    )
    width = video_info["width"]
    height = video_info["height"]

    new_width = int(width * zoom_factor)
    new_height = int(height * zoom_factor)
    x = (width - new_width) // 2 if center else 0
    y = (height - new_height) // 2 if center else 0

    stream = ffmpeg.input(input_file)
    stream = ffmpeg.crop(stream, x, y, new_width, new_height)

    with time_log("render_zoomed_video"):
        ffmpeg.output(stream, output_file).run(overwrite_output=True, quiet=True)


def speed_up_video(input_file: str, output_file: str, speed_factor: float = 10):
    """
    動画の速度を指定の倍率で上げる。
    """
    stream = ffmpeg.input(input_file)
    accelerated = ffmpeg.filter(stream, "setpts", f"PTS/{speed_factor}")

    with time_log("speed_up_video"):
        ffmpeg.output(accelerated, output_file).run(overwrite_output=True, quiet=True)


# if __name__ == "__main__":
#     input_files = [
#         "sample/20221002_184909_0.ts",
#         "sample/20221002_184909_0.ts",
#         "sample/20221002_190128_0.ts",
#         "sample/20221002_190422_0.ts",
#         "sample/20221002_190913_0.ts",
#         "sample/20221002_194853_0.ts",
#         "sample/20221002_195343_0.ts",
#     ]
#
#     output_file = "output.mp4"
#
#     combine_videos(input_files, output_file)
#     speed_up_video(output_file, "output_sppedup.mp4", 10)
#     render_zoomed_video(
#         "output_sppedup.mp4", "output_zoomed.mp4", zoom_factor=0.84, center=True
#     )
