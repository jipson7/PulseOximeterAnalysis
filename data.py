import pyrebase
from datetime import datetime
import pandas as pd

config = {
  "apiKey": "AIzaSyBKkJ72xZVPA8CX4ETB2YVZ4gcBAfv1mIU",
  "authDomain": "pulseoximeterapp.firebaseapp.com",
  "databaseURL": "https://pulseoximeterapp.firebaseio.com",
  "storageBucket": "pulseoximeterapp.appspot.com"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()


def create_date_from_millis(millis):
    if millis is not None:
        return datetime.fromtimestamp(millis / 1000.0)
    return None


class Device:

    data_collection = "data"
    df = None

    # Keys
    HR = 'hr'
    O2 = 'oxygen'
    RED_LED = 'red_led'
    IR_LED = 'ir_led'

    headers = [HR, O2, RED_LED, IR_LED]

    def __init__(self, device_data):
        self.description = device_data['description']
        self.name = device_data['name']
        self.user_description = device_data.get('user_description', None)
        self._create_data_frame(device_data['data'])

    def __str__(self):
        s = self.description
        if self.user_description is not None:
            s += " : " + self.user_description
        return s

    def _create_data_frame(self, data):
        print("Creating data frame...")
        indices = []
        data_list = []
        for key, readings in data.items():
            timestamp, values = self._extract_row(readings)
            indices.append(timestamp)
            data_list.append(values)
        self.df = pd.DataFrame(data_list, columns=self.headers, index=indices)
        print("Data frame created.")

    def _extract_row(self, readings):
        t = pd.to_datetime(readings['timestamp'], unit='ms')
        hr = readings.get(self.HR, None)
        o2 = readings.get(self.O2, None)
        red = readings.get(self.RED_LED, None)
        ir = readings.get(self.IR_LED, None)
        return t, [hr, o2, red, ir]


class Trial:

    devices = None

    def __init__(self, trial_doc):
        self.key = trial_doc.key()
        trial_data = trial_doc.val()
        self.start_date = create_date_from_millis(trial_data['start'])
        self.start_string = trial_data['date']
        self.end_date = create_date_from_millis(trial_data.get('end', None))
        self.description = trial_data['desc']

    def __str__(self):
        return self.start_string + " - " + self.description

    def load(self):
        device_docs = db.child("trials-data").child(self.key).child("devices").get()
        devices = []
        for doc in device_docs.each():
            devices.append(Device(doc.val()))
        self.devices = devices


def fetch_trials():
    trials = []
    trial_docs = db.child('trials').get()
    for trial_doc in trial_docs.each():
        trials.append(Trial(trial_doc))
    return trials
