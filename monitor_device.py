import argparse
import os
import shutil
from loguru import logger
from ts_convertor import aggregate_ts_files, speed_up_ts_file
from model.movie_filename import MovieFilename
import tempfile


def process_ts_files(monitor_volume_path: str, usb_name: str, movie_target_path: str):
    sd_card_path = os.path.join(monitor_volume_path, usb_name, movie_target_path)
    if not os.path.exists(sd_card_path):
        logger.error(f"Path does not exist: {sd_card_path}")
        return

    # Process front and rear videos separately
    front_videos_path = os.path.join(sd_card_path, "front")
    rear_videos_path = os.path.join(sd_card_path, "rear")

    if not os.path.exists(front_videos_path):
        logger.warning(f"Front videos path does not exist: {front_videos_path}")
    if not os.path.exists(rear_videos_path):
        logger.warning(f"Rear videos path does not exist: {rear_videos_path}")

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Aggregate and speed up front camera TS files by date
    aggregate_and_speed_up(
        front_videos_path, os.path.join(output_dir, "front"), speed_factor=10.0
    )

    # Aggregate and speed up rear camera TS files by date
    aggregate_and_speed_up(
        rear_videos_path, os.path.join(output_dir, "rear"), speed_factor=10.0
    )


def aggregate_and_speed_up(
    input_dir: str, output_base_path: str, speed_factor: float = 10.0
):
    if not os.path.exists(input_dir):
        logger.warning(f"Input directory does not exist: {input_dir}")
        return

    ts_files = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".ts")
    ]

    if not ts_files:
        logger.warning(f"No .ts files found in {input_dir}")
        return

    # Group TS files by date
    grouped_files = {}
    for ts_file in ts_files:
        try:
            filename = os.path.basename(ts_file)
            movie = MovieFilename(ts_file)
            date = movie.date
            if date not in grouped_files:
                grouped_files[date] = []
            grouped_files[date].append(ts_file)
        except MovieFilename.MovieFilenameError as e:
            logger.error(f"Skipping file due to error: {e}")

    for date, files in grouped_files.items():
        sorted_files = sorted(files)
        aggregated_output_file = f"{output_base_path}_{date}.ts"
        logger.info(
            f"Aggregating {len(sorted_files)} files for date {date} into {aggregated_output_file}"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Copying files to temporary directory: {temp_dir}")
            # Copy files to temp directory
            for file in sorted_files:
                shutil.copy(file, temp_dir)

            temp_files = [
                os.path.join(temp_dir, os.path.basename(f)) for f in sorted_files
            ]

            # Aggregate TS files from temp directory
            aggregate_ts_files(temp_files, aggregated_output_file)

        # After aggregation, speed up the aggregated file
        speedup_output_file = f"{output_base_path}_{date}_speedup.ts"
        logger.info(f"Speeding up {aggregated_output_file} to {speedup_output_file}")
        speed_up_ts_file(
            aggregated_output_file, speedup_output_file, speed_factor=speed_factor
        )

        # Replace the original aggregated file with the speedup file
        os.remove(aggregated_output_file)
        os.rename(speedup_output_file, aggregated_output_file)
        logger.info(f"Successfully created speedup file: {aggregated_output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Process TS files from external device."
    )
    parser.add_argument(
        "--monitor_volume_path",
        default="/Volumes",
        type=str,
        help="Directory where the external device is mounted.",
    )
    parser.add_argument(
        "--usb_name",
        default="MyDriveUSB",
        type=str,
        help="Name of the USB drive.",
    )
    parser.add_argument(
        "--movie_target_path",
        default="video",
        type=str,
        help="Directory containing the video files on the USB drive.",
    )

    args = parser.parse_args()
    process_ts_files(args.monitor_volume_path, args.usb_name, args.movie_target_path)


if __name__ == "__main__":
    main()
