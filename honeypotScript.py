import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
LOG_FILE_PATH = '/var/log/cowrie/cowrie.json'  # Path to the log file
API_ENDPOINT = 'http://16.171.142.151:3000/item'  # API endpoint to send log data

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(self.file_path, 'r')
        self.file.seek(0, 2)  # Move the cursor to the end of the file

    def on_modified(self, event):
        if event.src_path == self.file_path:
            self.send_new_lines()

    def send_new_lines(self):
        while True:
            line = self.file.readline()
            if not line:
                break
            self.send_to_api(line.strip())

    def send_to_api(self, log_data):
      print(log_data)
        response = requests.post(API_ENDPOINT, json={'log': log_data})
        if response.status_code == 200:
            print(f"Successfully sent log: {log_data}")
        else:
            print(f"Failed to send log: {log_data}, Status Code: {response.status_code}")

if __name__ == "__main__":
    event_handler = LogFileHandler(LOG_FILE_PATH)
    observer = Observer()
    observer.schedule(event_handler, path=LOG_FILE_PATH, recursive=False)
    observer.start()
    print(f"Monitoring {LOG_FILE_PATH} for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
