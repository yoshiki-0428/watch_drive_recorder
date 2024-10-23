import os
import re


class MovieFilename:
    class MovieFilenameError(Exception):
        pass

    def __init__(self, filename: str):
        _name = os.path.basename(filename).split(".")[0]

        if len(_name.split("_")) < 3:
            raise MovieFilename.MovieFilenameError(f"Invalid filename: {filename}")

        # Check if the date format is correct using regex
        if not re.match(r"\d{8}", _name.split("_")[0]):
            raise MovieFilename.MovieFilenameError(
                f"Invalid date format in filename: {filename}"
            )

        self.origin = filename
        self.file_type = filename.split(".")[1]
        self.date: str = _name.split("_")[0]
        self.time: str = _name.split("_")[1]
        self.datetime: str = self.date + "_" + self.time
        self.camera_type: str = _name.split("_")[2]

    def is_file_type(self, check_type: str = "mp4"):
        return self.file_type == check_type

    def is_front_camera(self):
        return self.camera_type == "0"

    def is_rear_camera(self):
        return self.camera_type == "1"
