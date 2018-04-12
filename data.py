import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from collections import OrderedDict
import pandas as pd


def create_date_from_millis(millis):
    return datetime.fromtimestamp(millis / 1000.0)


class Device:

    data_collection = "data"
    data_sets = {}

    # Keys
    HR = 'hr'
    O2 = 'oxygen'
    RED_LED = 'red_led'
    IR_LED = 'ir_led'

    headers = ['timestamp', HR, O2, RED_LED, IR_LED]

    def __init__(self, document):
        data = document.to_dict()
        self.description = data['description']
        self.name = data['name']
        self.user_description = data['user_description']
        self.data_ref = document.reference.collection(self.data_collection)

    def __str__(self):
        s = self.description
        if self.user_description is not None:
            s += " : " + self.user_description
        return s

    def get_data(self):
        print("Loading data...")
        data_docs = self.data_ref.get()
        result = []
        for doc in data_docs:
            row = self._extract_row(doc)
            result.append(row)
        print("Data Loaded. Creating Data Frame...")
        return pd.DataFrame(result, columns=self.headers)

    def _extract_row(self, doc):
        data = doc.to_dict()
        t = int(doc.id)
        hr = data.get(self.HR, None)
        o2 = data.get(self.O2, None)
        red = data.get(self.RED_LED, None)
        ir = data.get(self.IR_LED, None)
        return [t, hr, o2, red, ir]


class Trial:

    devices_collection = "devices"

    def __init__(self, document):
        data = document.to_dict()
        self.start_date = create_date_from_millis(data['start'])
        self.start_string = data['date']
        self.end_date = create_date_from_millis(data['end'])
        self.description = data['desc']
        self.device_ref = document.reference.collection(self.devices_collection)

    def get_devices(self):
        print("Loading Devices...")
        device_docs = self.device_ref.get()
        devices = []
        for doc in device_docs:
            devices.append(Device(doc))
        return devices

    def __str__(self):
        return self.start_string + " - " + self.description


class Loader:

    trials_collection = 'trials'
    project_id = 'pulseoximeterapp'

    def __init__(self):
        cred = credentials.Certificate('./credentials.json')
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def get_trials(self):
        trials = []
        trial_docs = self.db.collection(self.trials_collection).get()
        for doc in trial_docs:
            trials.append(Trial(doc))
        return trials

