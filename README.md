# Command

## monitor_device.py

Monitor the USB device and copy the video files to the target directory.

```shell
python monitor_device.py --monitor_volume_path "/Volumes" --usb_name "CARDRIVE" --movie_target_path "video"
```

## upload_video.py

Launch the script with the following command:

This script is run every day at 2:00 AM. It uploads the videos from the output directory to the archive directory.

```shell
python upload_videos.py --output_dir "output" --archive_dir "archive" --upload_time "02:00"
```
