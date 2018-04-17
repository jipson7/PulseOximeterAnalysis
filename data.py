import pyrebase
from datetime import datetime
import pandas as pd
import keys

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

    headers = [keys.HR, keys.O2, keys.RED_LED, keys.IR_LED]

    def __init__(self, device_data):
        self.description = device_data['description']
        self.name = device_data['name']
        self.graph_name = self._get_graph_name()
        self.user_description = device_data.get('user_description', None)
        self._create_data_frame(device_data['data'])

    def _get_graph_name(self):
        if self.name == 'USBUART':
            return 'Ground Truth'
        elif self.name == 'Flora':
            return 'MAX30102 Sensor'
        else:
            raise Exception('Device does not yet have a graph name! Set one!')

    def __str__(self):
        s = self.description
        if self.user_description is not None:
            s += " : " + self.user_description
        return s

    def _create_data_frame(self, data):
        print("Creating data frame...")
        timestamps = []
        data_list = []
        for key, readings in data.items():
            timestamp, values = self._extract_row(readings)
            timestamps.append(timestamp)
            data_list.append(values)
        assert(len(timestamps) == len(set(timestamps)))  # No Duplicates
        if sorted(timestamps) != timestamps:
            print("Timestamps are not sorted. Sorting.")
            timestamps, data_list = (list(t) for t in zip(*sorted(zip(timestamps, data_list))))
        assert(sorted(timestamps) == timestamps)
        indices = pd.to_datetime(timestamps, unit='ms')
        self.df = pd.DataFrame(data_list, columns=self.headers, index=indices)
        print("Data frame created.")

    def _extract_row(self, readings):
        t = readings[keys.TIMESTAMP]
        hr = readings.get(keys.HR, None)
        o2 = readings.get(keys.O2, None)
        red = readings.get(keys.RED_LED, None)
        ir = readings.get(keys.IR_LED, None)
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
