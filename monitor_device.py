import argparse
import os
from loguru import logger
from ts_convertor import aggregate_ts_files
from model.movie_filename import MovieFilename


def process_ts_files(monitor_volume_path: str, usb_name: str, movie_target_path: str):
    sd_card_path = os.path.join(
        monitor_volume_path,
        usb_name,
        movie_target_path
    )
    if not os.path.exists(sd_card_path):
        logger.error(f"Path does not exist: {sd_card_path}")
        return

    # Process front and rear videos separately
    front_videos_path = os.path.join(sd_card_path, 'front')
    rear_videos_path = os.path.join(sd_card_path, 'rear')

    if not os.path.exists(front_videos_path):
        logger.warning(f"Front videos path does not exist: {front_videos_path}")
    if not os.path.exists(rear_videos_path):
        logger.warning(f"Rear videos path does not exist: {rear_videos_path}")

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Aggregate front camera TS files by date
    aggregate_ts_files_by_date(front_videos_path, os.path.join(output_dir, 'front'))

    # Aggregate rear camera TS files by date
    aggregate_ts_files_by_date(rear_videos_path, os.path.join(output_dir, 'rear'))


def aggregate_ts_files_by_date(input_dir: str, output_base_path: str):
    if not os.path.exists(input_dir):
        logger.warning(f"Input directory does not exist: {input_dir}")
        return

    ts_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.endswith('.ts')
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
        output_file = f"{output_base_path}_{date}.ts"
        logger.info(f"Aggregating {len(sorted_files)} files for date {date} into {output_file}")
        aggregate_ts_files(sorted_files, output_file)


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
    process_ts_files(
        args.monitor_volume_path, args.usb_name, args.movie_target_path
    )


if __name__ == "__main__":
    main()
