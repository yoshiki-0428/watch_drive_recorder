import re
import os


class MovieFilename:
    class MovieFilenameError(Exception):
        pass

    def __init__(self, filepath: str):
        filename = os.path.basename(filepath)
        _name = filename.split(".")[0]

        if len(_name.split("_")) < 3:
            raise MovieFilename.MovieFilenameError(f"Invalid filename: {filename}")

        # 日付が正しいフォーマットかチェック（YYYYMMDD）
        date_part = _name.split("_")[0]
        if not re.match(r"^\d{8}$", date_part):
            raise MovieFilename.MovieFilenameError(
                f"Invalid date format in filename: {filename}"
            )

        self.origin = filename
        self.file_type = filename.split(".")[1]
        self.date: str = date_part
        self.time: str = _name.split("_")[1]
        self.datetime: str = f"{self.date}_{self.time}"
        self.camera_type: str = _name.split("_")[2]

    def is_file_type(self, check_type: str = "ts"):
        return self.file_type.lower() == check_type.lower()

    def is_front_camera(self):
        return self.camera_type == "0"

    def is_rear_camera(self):
        return self.camera_type == "1"
