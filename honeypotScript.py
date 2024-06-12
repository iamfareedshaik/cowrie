import json
import time
import os
import http.client
import pyinotify

# Configuration
LOG_FILE_PATH = '/home/cowrie/cowrie/var/log/cowrie/cowrie.json'
API_HOST = '16.171.142.151'
API_PORT = 3000
API_ENDPOINT = '/item'

class LogFileHandler(pyinotify.ProcessEvent):
    def my_init(self, file_path):
        self.file_path = file_path

    def process_IN_MODIFY(self, event):
        if event.pathname == self.file_path:
            self.send_new_lines()

    def send_new_lines(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                self.send_to_api(line.strip())

    def send_to_api(self, log_data):
        print("---------------------------------")
        print(log_data)
        print("--------------------------------")
        connection = http.client.HTTPConnection(API_HOST, API_PORT)
        headers = {'Content-type': 'application/json'}
        log_data = {'log': log_data}
        connection.request('POST', API_ENDPOINT, headers=headers, body=json.dumps(log_data))
        response = connection.getresponse()
        if response.status == 200:
            print(f"Successfully sent log: {log_data}")
        else:
            print(f"Failed to send log: {log_data}, Status Code: {response.status}")

if __name__ == "__main__":
    # Wait for the log file to be created
    print("welcome")
    while not os.path.exists(LOG_FILE_PATH):
        print(f"Waiting for {LOG_FILE_PATH} to be created...")
        time.sleep(30)

    wm = pyinotify.WatchManager()
    handler = LogFileHandler(file_path=LOG_FILE_PATH)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(LOG_FILE_PATH, pyinotify.IN_MODIFY)

    print(f"Monitoring {LOG_FILE_PATH} for changes...")

    try:
        notifier.loop()
    except KeyboardInterrupt:
        notifier.stop()
