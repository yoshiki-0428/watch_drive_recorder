import os
import time
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from ts_convertor import convert_ts_file


class ExternalDeviceEventHandler(FileSystemEventHandler):
    def __init__(self, monitor_volume_path: str, usb_name: str, movie_target_path: str):
        super().__init__()
        self.monitor_volume_path = monitor_volume_path
        self.usb_name = usb_name
        self.movie_target_path = movie_target_path

    def on_any_event(self, event: FileSystemEvent) -> None:
        print(f"Event Start: {event.event_type} {event.src_path}")
        # 監視対象のフォルダだった場合, TSファイルの変換・整理の処理を行う
        if event.dest_path.endswith(self.usb_name):
            sd_card_path = os.path.join(self.monitor_volume_path, self.usb_name, *os.path.splitext(self.movie_target_path))
            convert_ts_file(sd_card_path)


def monitor_external_device(monitor_volume_path: str, usb_name: str, movie_target_path: str):
    event_handler = ExternalDeviceEventHandler(monitor_volume_path, usb_name, movie_target_path)
    observer: Observer = Observer()
    observer.schedule(event_handler, monitor_volume_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main():
    parser = argparse.ArgumentParser(description="Monitor external device and execute command on connection.")
    parser.add_argument("--monitor_volume_path", default="/Volumes", type=str, help="This is monitor directory.")
    parser.add_argument("--usb_name", default="MyDriveUSB", type=str, help="This is usb name.")
    parser.add_argument("--movie_target_path", default="movie/drive", type=str, help="This is has movie target directory name.")

    args = parser.parse_args()
    monitor_external_device(args.monitor_volume_path, args.usb_name, args.movie_target_path)

if __name__ == "__main__":
    main()
