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
            "copy",
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
