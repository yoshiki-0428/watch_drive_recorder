import re


class MovieFilename:
    class MovieFilenameError(Exception):
        pass

    def __init__(self, filename: str):
        _name = filename.split(".")[0]
        # listの末尾を取得する
        name = _name.split("/")[-1]

        if len(name.split("_")) < 3:
            raise MovieFilename.MovieFilenameError(f"Invalid filename: {filename}")

        # 日付かどうか正規表現でチェック
        if not re.match(r"\d{8}", name.split("_")[0]):
            raise MovieFilename.MovieFilenameError(
                f"Invalid filename by date format: {filename}"
            )

        self.origin = filename
        self.file_type = filename.split(".")[1]
        self.date: str = name.split("_")[0]
        self.time: str = name.split("_")[1]
        self.datatime: str = self.date + "_" + self.time
        self.type: str = name.split("_")[2]

    def is_file_type(self, check_type: str = "mp4"):
        if self.file_type == check_type:
            return True
        return False

    def is_front_camera(self):
        if self.type == "0":
            return True
        return False

    def is_rear_camera(self):
        if self.type == "1":
            return True
        return False
