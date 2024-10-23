import os
from loguru import logger
import subprocess


def aggregate_ts_files(ts_files: list, output_file: str):
    if not ts_files:
        logger.warning("No TS files to aggregate.")
        return

    # Create a temporary file list for ffmpeg
    list_file_path = "file_list.txt"
    with open(list_file_path, "w") as f_list:
        for ts_file in ts_files:
            # ffmpeg requires paths to be properly escaped
            escaped_path = ts_file.replace("'", r"'\''")
            f_list.write(f"file '{escaped_path}'\n")

    try:
        # Use ffmpeg to concatenate ts files
        command = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file_path,
            "-c",
            "copy",  # Copy codecs since we're just concatenating
            output_file,
        ]
        logger.info(f"Running command: {' '.join(command)}")
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if result.returncode != 0:
            logger.error(f"ffmpeg failed with error: {result.stderr}")
        else:
            logger.info(f"Successfully created {output_file}")
    except Exception as e:
        logger.error(f"Exception during ffmpeg execution: {e}")
    finally:
        # Clean up the temporary file list
        if os.path.exists(list_file_path):
            os.remove(list_file_path)


def speed_up_ts_file(
    input_file: str,
    output_file: str,
    speed_factor: float = 10.0,
    disable_audio: bool = True,
):
    """
    Speeds up a TS file by the given speed factor, utilizing hardware acceleration.
    Optionally disables audio to speed up the process.

    :param input_file: Path to the input TS file.
    :param output_file: Path to the output speedup TS file.
    :param speed_factor: Factor by which to speed up the video.
    :param disable_audio: If True, audio stream will be disabled to speed up processing.
    """
    if not os.path.exists(input_file):
        logger.error(f"Input file does not exist: {input_file}")
        return

    # Calculate setpts value for video
    setpts = f"PTS/{speed_factor}"

    # Prepare audio filters if audio is to be processed
    if not disable_audio:
        # Calculate atempo filters for audio
        # atempo supports a max of 2.0 per filter, so chain multiple filters
        atempo_filters = []
        remaining_speed = speed_factor
        while remaining_speed > 2.0:
            atempo_filters.append("atempo=2.0")
            remaining_speed /= 2.0
        atempo_filters.append(f"atempo={remaining_speed}")
        atempo_filter = ",".join(atempo_filters)
        audio_filter = f"[0:a]{atempo_filter}[a]"
    else:
        audio_filter = ""

    # Choose codec: use hardware acceleration if available
    # For macOS, use 'h264_videotoolbox'
    video_codec = "h264_videotoolbox"

    # Set encoding preset to 'ultrafast' for maximum speed
    preset = "ultrafast"

    # Build filter_complex
    if disable_audio:
        filter_complex = f"[0:v]setpts={setpts}[v]"
    else:
        filter_complex = f"[0:v]setpts={setpts}[v];{audio_filter}"

    # Build the ffmpeg command
    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        # Map audio if not disabled
    ]

    if not disable_audio:
        command += ["-map", "[a]"]

    command += [
        "-c:v",
        video_codec,  # Use hardware acceleration for video
        "-preset",
        preset,  # Set encoding preset to ultrafast
    ]

    if not disable_audio:
        command += [
            "-c:a",
            "aac",  # Encode audio with AAC
            "-b:a",
            "64k",  # Set low bitrate for faster encoding
        ]

    command += [output_file]

    if disable_audio:
        # Disable audio
        command.insert(-1, "-an")

    try:
        logger.info(f"Running speed-up command: {' '.join(command)}")
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if result.returncode != 0:
            logger.error(f"ffmpeg speed-up failed with error: {result.stderr}")
        else:
            logger.info(f"Successfully created speedup file: {output_file}")
    except Exception as e:
        logger.error(f"Exception during ffmpeg speed-up execution: {e}")
