import os
import re
import shutil
import time

import ffmpeg
import argparse
from typing import Dict, List

from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip


OUTPUT_DIR = "output"
COMBINED_OUTPUT_DIR = "output_combined"
FILTER_DURATION = 20


class MovieFilename:
    class MovieFilenameError(Exception):
        pass

    def __init__(self, filename: str):
        name = filename.split(".")[0]
        if len(name.split("_")) < 3:
            raise MovieFilename.MovieFilenameError(f"Invalid filename: {filename}")

        # 日付かどうか正規表現でチェック
        if not re.match(r"\d{8}", name.split("_")[0]):
            raise ValueError(f"Invalid filename by date format: {filename}")

        self.origin = filename
        self.file_type = filename.split(".")[1]
        self.date = name.split("_")[0]
        self.time = name.split("_")[1]
        self.type = name.split("_")[2]

    def is_file_type(self, check_type: str = "mp4"):
        if self.file_type == check_type:
            return True
        return False

    def is_front_camera(self):
        if self.type == "0":
            return True
        return False


class TSFileConvertor:
    class TSFileIsEmpty(Exception):
        pass

    def __init__(
        self,
        sd_card_path: str,
        output_dir: str = OUTPUT_DIR,
        combine_output_dir: str = COMBINED_OUTPUT_DIR,
    ):
        self.sd_card_path = sd_card_path
        self.output_dir: str = output_dir
        self.combine_output_dir: str = combine_output_dir

        # Filter the files to only include TS files and time check
        self.__filter_ts_files()

        abs_sd_path = os.path.abspath(sd_card_path)
        files = []
        for file in os.listdir(abs_sd_path):
            if os.path.isfile(os.path.join(abs_sd_path, file)):
                files.append(os.path.join(abs_sd_path, file))

        ts_files = [file for file in files if file.endswith(".ts")]
        if len(ts_files) == 0:
            raise TSFileConvertor.TSFileIsEmpty("No TS files found. Exiting...")

        self.ts_files = ts_files

        # output_dir がない場合はmakedirする
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # combine_output_dir がない場合はmakedirする
        if not os.path.exists(combine_output_dir):
            os.makedirs(combine_output_dir)

    def convert(self) -> None:
        print(f"Founded {len(self.ts_files)} TS files. Convert is starting...")

        # Process each TS file
        self.__ts2mp4()

        # Group MP4 files by day
        self.__group_mp4_files_by_day()

        # Delete ts file
        [os.remove(file) for file in self.ts_files]

    def __filter_ts_files(self, filter_duration: float = FILTER_DURATION) -> None:
        for filename in os.listdir(self.sd_card_path):
            if filename.endswith(".ts"):
                file_path = os.path.join(self.sd_card_path, filename)
                probe = ffmpeg.probe(file_path)
                duration = float(probe["format"]["duration"])

                # Delete MP4 files that are 10 seconds or less
                if duration <= filter_duration:
                    os.remove(file_path)
                    print(f"Deleted {file_path} (duration: {duration} seconds)")

    def __ts2mp4(self) -> None:
        current = 1
        for input_file in self.ts_files:
            output_file = os.path.join(
                self.output_dir,
                os.path.splitext(os.path.basename(input_file))[0] + ".mp4",
            )

            # Convert the TS file to MP4
            print(f"{current} / {len(self.ts_files)}")
            print(
                f"File name: {output_file}. Output: {output_file}. Convert is starting. "
            )
            ffmpeg.input(input_file).output(output_file).run(
                overwrite_output=True, quiet=True
            )
            print(f"File name: {output_file}. Convert is end. ")
            current += 1

    def __group_mp4_files_by_day(self) -> None:
        """
        日ごとに分けてMP4ファイルを結合する

        :return: None
        """
        files_by_date: Dict[str, List[MovieFilename]] = {}

        # Group files by creation date
        for _filename in os.listdir(self.output_dir):
            try:
                movie_file = MovieFilename(_filename)
            except MovieFilename.MovieFilenameError as e:
                print(e)
                continue

            if movie_file.is_file_type("mp4"):
                date_str = movie_file.date
                if date_str not in files_by_date:
                    files_by_date[date_str] = []

                if movie_file.is_front_camera():
                    files_by_date[date_str].append(movie_file)

        print(f"Grouped files by date: {files_by_date}")

        # Combine files by date
        for date_str, file_list in files_by_date.items():
            # 1つの場合は 日付.mp4でoutputからファイル移動をする
            if len(file_list) <= 1:
                shutil.move(
                    os.path.join(self.output_dir, file_list[0].origin),
                    os.path.join(self.combine_output_dir, f"{date_str}.mp4"),
                )
                print(
                    f"Moved {file_list[0]} to {os.path.join(self.output_dir, f'{date_str}.mp4')}"
                )

            else:
                video_clips = []
                for video in sorted(file_list, key=lambda x: x.time):
                    video_clips.append(
                        VideoFileClip(os.path.join(self.output_dir, video.origin))
                    )

                try:
                    complete_clip: CompositeVideoClip = concatenate_videoclips(
                        video_clips, method="compose"
                    )
                    complete_clip.write_videofile(
                        os.path.join(self.combine_output_dir, f"{date_str}.mp4"),
                        fps=30,
                        codec="libx264",
                        audio_codec="aac",
                    )
                    print(
                        f"Combined files for {date_str} into {os.path.join(self.output_dir, f"{date_str}.mp4")}"
                    )

                except Exception as e:
                    print(f"Error combining files for {date_str}: {e}")

                for video in file_list:
                    os.remove(os.path.join(self.output_dir, video.origin))


def convert_ts_file(sd_card_path: str) -> None:
    print(f"Converting TS files in {sd_card_path}...")
    abs_sd_path = os.path.abspath(sd_card_path)
    files = []
    for file in os.listdir(abs_sd_path):
        if os.path.isfile(os.path.join(abs_sd_path, file)):
            files.append(os.path.join(abs_sd_path, file))

    try:
        convertor: TSFileConvertor = TSFileConvertor(sd_card_path)
        convertor.convert()

    except TSFileConvertor.TSFileIsEmpty as e:
        print(e)
    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor SD card and convert TS files to MP4."
    )
    parser.add_argument("sd_card_path", type=str, help="Path to the SD card directory.")

    args = parser.parse_args()

    convert_ts_file(args.sd_card_path)


if __name__ == "__main__":
    main()
