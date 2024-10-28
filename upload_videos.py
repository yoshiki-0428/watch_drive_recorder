# upload_videos.py

import os
import shutil
from loguru import logger
from youtube_uploader import authenticate_youtube, upload_video_to_youtube
from googleapiclient.errors import HttpError
import argparse
import schedule
import time


def upload_output_files(output_dir: str, youtube, archive_dir: str = "archive"):
    """
    outputディレクトリ内のファイルをチェックし、存在する場合にYouTubeにアップロードします。
    アップロードが成功したファイルはarchiveディレクトリに移動します。

    :param output_dir: 処理された動画ファイルが格納されているディレクトリ
    :param youtube: 認証済みのYouTubeサービスオブジェクト
    :param archive_dir: アップロード済みの動画ファイルを移動するディレクトリ
    """
    if not os.path.exists(output_dir):
        logger.error(f"Output directory does not exist: {output_dir}")
        return

    os.makedirs(archive_dir, exist_ok=True)

    processed_files = [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".ts")
        and not f.endswith("_speedup.ts")  # speedupファイルはリネーム済み
    ]

    if not processed_files:
        logger.warning(f"No processed .ts files found in {output_dir} for uploading.")
        return

    for video_file in processed_files:
        if os.path.exists(video_file):
            date_camera = os.path.splitext(os.path.basename(video_file))[
                0
            ]  # yyyymmdd_front または yyyymmdd_rear
            title = f"{date_camera} - Speeded Up Video"
            description = f"Speeded up video for {date_camera.split('_')[0]} from {date_camera.split('_')[1]} camera."
            logger.info(f"Uploading {video_file} to YouTube with title '{title}'")
            try:
                video_id = upload_video_to_youtube(
                    youtube, video_file, title, description
                )
                logger.info(f"Uploaded video to YouTube with ID: {video_id}")

                # アップロードが成功したら、ファイルをarchiveディレクトリに移動
                archived_file = os.path.join(archive_dir, os.path.basename(video_file))
                shutil.move(video_file, archived_file)
                logger.info(f"Moved uploaded video to archive: {archived_file}")

            except HttpError as e:
                if e.resp.status == 403:
                    logger.error(
                        "YouTube Data APIのクォータを超過しました。後ほど再試行してください。"
                    )
                else:
                    logger.error(f"Failed to upload video to YouTube: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred during upload: {e}")
        else:
            logger.error(f"Processed video file does not exist: {video_file}")


def scheduled_upload_task(output_dir: str, youtube, archive_dir: str = "archive"):
    """
    スケジュールされたタイミングでアップロードタスクを実行します。
    """
    logger.info("Scheduled upload task started.")
    upload_output_files(output_dir, youtube, archive_dir)
    logger.info("Scheduled upload task completed.")


def main():
    parser = argparse.ArgumentParser(
        description="Upload processed video files to YouTube once a day."
    )
    parser.add_argument(
        "--output_dir",
        default="output",
        type=str,
        help="Directory containing the processed video files.",
    )
    parser.add_argument(
        "--archive_dir",
        default="archive",
        type=str,
        help="Directory to archive uploaded video files.",
    )
    parser.add_argument(
        "--upload_time",
        default="02:00",
        type=str,
        help="Daily time to run the upload task (24-hour format, e.g., '02:00').",
    )

    args = parser.parse_args()

    # YouTube認証
    youtube = authenticate_youtube()

    # スケジュールの設定
    schedule.every().day.at(args.upload_time).do(
        scheduled_upload_task,
        output_dir=args.output_dir,
        youtube=youtube,
        archive_dir=args.archive_dir,
    )

    logger.info(f"Scheduler started. Upload task will run daily at {args.upload_time}.")

    # スケジューラのループ
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにスケジュールをチェック
    except KeyboardInterrupt:
        logger.info("Upload scheduler terminated by user.")


if __name__ == "__main__":
    # ログファイルの設定（オプション）
    logger.add(
        "upload_videos.log", rotation="10 MB", retention="10 days", compression="zip"
    )
    main()
