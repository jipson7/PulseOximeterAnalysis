import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime


def create_date_from_millis(millis):
    return datetime.fromtimestamp(millis / 1000.0)


class Device:

    def __init__(self, document):
        data = document.to_dict()
        self.description = data['description']
        self.name = data['name']
        self.user_description = data['user_description']

    def __str__(self):
        s = self.description
        if self.user_description is not None:
            s + " : " + self.user_description
        return s


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

    def fetch_trials(self):
        trials = []
        trial_docs = self.db.collection(self.trials_collection).get()
        for doc in trial_docs:
            trials.append(Trial(doc))
        return trials

