import argparse
import os
import shutil
from loguru import logger
from ts_convertor import aggregate_ts_files, speed_up_ts_file
from model.movie_filename import MovieFilename
import tempfile


def process_ts_files(
    monitor_volume_path: str, usb_name: str, movie_target_path: str, output_dir: str
):
    """
    USBドライブからTSファイルを処理し、指定された出力ディレクトリに保存します。

    :param monitor_volume_path: 外部デバイスがマウントされているディレクトリ
    :param usb_name: USBドライブの名前
    :param movie_target_path: USBドライブ内の動画ファイルが格納されているディレクトリ
    :param output_dir: 出力ファイルを保存するディレクトリ
    """
    sd_card_path = os.path.join(monitor_volume_path, usb_name, movie_target_path)
    if not os.path.exists(sd_card_path):
        logger.error(f"Path does not exist: {sd_card_path}")
        return

    # フロントとリアの動画ディレクトリを設定
    front_videos_path = os.path.join(sd_card_path, "front")
    rear_videos_path = os.path.join(sd_card_path, "rear")

    if not os.path.exists(front_videos_path):
        logger.warning(f"Front videos path does not exist: {front_videos_path}")
    if not os.path.exists(rear_videos_path):
        logger.warning(f"Rear videos path does not exist: {rear_videos_path}")

    os.makedirs(output_dir, exist_ok=True)

    # フロントカメラのTSファイルを集約・速度変更
    aggregate_and_speed_up(
        front_videos_path, output_dir, camera="front", speed_factor=10.0
    )

    # リアカメラのTSファイルを集約・速度変更
    aggregate_and_speed_up(
        rear_videos_path, output_dir, camera="rear", speed_factor=10.0
    )


def aggregate_and_speed_up(
    input_dir: str, output_dir: str, camera: str, speed_factor: float = 10.0
):
    """
    指定された入力ディレクトリ内のTSファイルを集約し、速度を変更して出力ディレクトリに保存します。

    :param input_dir: 入力TSファイルが格納されているディレクトリ
    :param output_dir: 出力ファイルを保存するディレクトリ
    :param camera: カメラの種類（例: "front", "rear"）
    :param speed_factor: 速度変更の倍率（デフォルトは10.0）
    """
    if not os.path.exists(input_dir):
        logger.warning(f"Input directory does not exist: {input_dir}")
        return

    ts_files = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".ts")
    ]

    if not ts_files:
        logger.warning(f"No .ts files found in {input_dir}")
        return

    # 日付ごとにTSファイルをグループ化
    grouped_files = {}
    for ts_file in ts_files:
        try:
            movie = MovieFilename(ts_file)
            date = movie.date
            if date not in grouped_files:
                grouped_files[date] = []
            grouped_files[date].append(ts_file)
        except MovieFilename.MovieFilenameError as e:
            logger.error(f"Skipping file due to error: {e}")

    for date, files in grouped_files.items():
        sorted_files = sorted(files)

        # ファイル名のルール: yyyymmdd_front.ts または yyyymmdd_rear.ts
        aggregated_output_file = os.path.join(output_dir, f"{date}_{camera}.ts")
        logger.info(
            f"Aggregating {len(sorted_files)} files for date {date} into {aggregated_output_file}"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Copying files to temporary directory: {temp_dir}")
            # 一時ディレクトリにファイルをコピー
            for file in sorted_files:
                shutil.copy(file, temp_dir)

            temp_files = [
                os.path.join(temp_dir, os.path.basename(f)) for f in sorted_files
            ]

            # 一時ディレクトリ内のTSファイルを集約
            aggregate_ts_files(temp_files, aggregated_output_file)

        # 速度変更後のファイル名
        speedup_output_file = os.path.join(output_dir, f"{date}_{camera}_speedup.ts")
        logger.info(f"Speeding up {aggregated_output_file} to {speedup_output_file}")
        speed_up_ts_file(
            aggregated_output_file, speedup_output_file, speed_factor=speed_factor
        )

        # 速度変更が成功した場合、元の集約ファイルを削除し、速度変更ファイルにリネーム
        if os.path.exists(speedup_output_file):
            os.remove(aggregated_output_file)
            os.rename(speedup_output_file, aggregated_output_file)
            logger.info(f"Successfully created speedup file: {aggregated_output_file}")

            # 処理が成功したら、元のソース `.ts` ファイルを削除
            logger.info(f"Deleting source .ts files for date {date}")
            for file in sorted_files:
                try:
                    os.remove(file)
                    logger.debug(f"Deleted file: {file}")
                except Exception as e:
                    logger.error(f"Failed to delete file {file}: {e}")
        else:
            logger.error(
                f"Speed-up failed for {aggregated_output_file}. Original aggregated file not deleted."
            )


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
    parser.add_argument(
        "--output_dir",
        default="output",
        type=str,
        help="Directory where the processed video files will be saved.",
    )

    args = parser.parse_args()
    process_ts_files(
        args.monitor_volume_path, args.usb_name, args.movie_target_path, args.output_dir
    )


if __name__ == "__main__":
    # ログファイルの設定（オプション）
    logger.add(
        "process_device.log", rotation="10 MB", retention="10 days", compression="zip"
    )
    main()
