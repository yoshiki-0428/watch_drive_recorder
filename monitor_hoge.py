import subprocess
import time
import re


def monitor_usb_device(command):
  previous_devices = set()
  while True:
    result = subprocess.run(['diskutil', 'list'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    print(output)

    current_devices = set(re.findall(r'/dev/disk\d+', output))
    new_devices = current_devices - previous_devices

    if new_devices:
      for device in new_devices:
        print(f"USB device connected: {device}")
        subprocess.run(command, shell=True)
        print("Processing completed.")

    previous_devices = current_devices
    time.sleep(1)


if __name__ == "__main__":
  command = "your_command_here"
  monitor_usb_device(command)
