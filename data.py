import pyrebase
import datetime
import pandas as pd
import keys
import numpy as np
import pickle

import os.path

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
        return datetime.datetime.fromtimestamp(millis / 1000.0)
    return None


def get_common_endpoints(df1, df2):
    df_start = df1.index[0] if (df1.index[0] > df2.index[0]) else df2.index[0]
    df_end = df1.index[-1] if (df1.index[-1] < df2.index[-1]) else df2.index[-1]
    return df_start, df_end


class Device:

    data_collection = "data"
    df = None

    headers = [keys.HR, keys.O2, keys.RED_LED, keys.IR_LED]

    def __init__(self, device_data):
        self.description = device_data['description']
        self.name = device_data['name']
        self.user_description = device_data.get('user_description', None)
        self._create_data_frame(device_data['data'])

    def __str__(self):
        result = ''
        if self.name == 'USBUART':
            result += 'Ground Truth'
        elif self.name == 'Flora':
            result += 'MAX30102 Sensor'
        else:
            raise Exception('Device does not yet have a graph name! Set one!')
        result += ' - ' + self.user_description
        return result

    def _create_data_frame(self, data):
        timestamps = []
        data_list = []
        for key, readings in data.items():
            timestamp, values = self._extract_row(readings)
            timestamps.append(timestamp)
            data_list.append(values)
        assert(len(timestamps) == len(set(timestamps)))  # No Duplicates
        if sorted(timestamps) != timestamps:
            timestamps, data_list = (list(t) for t in zip(*sorted(zip(timestamps, data_list))))
        assert(sorted(timestamps) == timestamps)
        indices = pd.to_datetime(timestamps, unit='ms')
        self.df = pd.DataFrame(data_list, columns=self.headers, index=indices)

    def _extract_row(self, readings):
        t = readings[keys.TIMESTAMP]
        hr = readings.get(keys.HR, None)
        o2 = readings.get(keys.O2, None)
        red = readings.get(keys.RED_LED, None)
        ir = readings.get(keys.IR_LED, None)
        return t, [hr, o2, red, ir]

    def convert_index_to(self, type):
        self.df = self.df.set_index(self.df.index.astype(type))


class Trial:

    devices = None

    def __init__(self, trial_doc):
        self.key = trial_doc.key()
        trial_data = trial_doc.val()
        self.start_date = create_date_from_millis(trial_data['start'])
        self.start_string = trial_data['date']
        self.end_date = create_date_from_millis(trial_data.get('end', None))
        self.description = trial_data['desc']
        self.pickle_path = 'cache/' + str(self.start_date)

    def __str__(self):
        return self.start_string + " - " + self.description

    def load(self):
        if os.path.isfile(self.pickle_path):
            print("Loading data from pickle")
            self.devices = pickle.load(open(self.pickle_path, 'rb'))
        else:
            print("Loading data from server")
            device_docs = db.child("trials-data").child(self.key).child("devices").get()
            devices = []
            for doc in device_docs.each():
                devices.append(Device(doc.val()))
            self.devices = devices
            self._normalize_device_timestamps()
            self._pickle()
        print("Data loaded.")

    def _pickle(self):
        print("Pickling data.")
        pickle.dump(self.devices, open(self.pickle_path, 'wb'))

    def _normalize_device_timestamps(self):
        print("Normalizing dataframes between devices")
        sample_range = datetime.timedelta(milliseconds=40)
        d1 = self.devices[0]
        d2 = self.devices[1]
        indices = []
        new_data1 = []
        new_data2 = []
        df_start, df_end = get_common_endpoints(d1.df, d2.df)
        sample_date = df_start
        while sample_date < df_end:
            data1 = d1.df.iloc[d1.df.index.get_loc(sample_date, method='nearest')].values
            data2 = d2.df.iloc[d2.df.index.get_loc(sample_date, method='nearest')].values
            indices.append(sample_date)
            new_data1.append(data1)
            new_data2.append(data2)
            sample_date += sample_range
        new_df1 = pd.DataFrame(data=new_data1, index=indices, columns=d1.df.columns.values)
        new_df2 = pd.DataFrame(data=new_data2, index=indices, columns=d2.df.columns.values)
        self.devices[0].df = new_df1
        self.devices[1].df = new_df2

    def device_combinations(self):
        from itertools import combinations
        return combinations(self.devices, 2)

    def delete(self):
        print("Deleting " + str(self))
        db.child("trials-data").child(self.key).remove()
        db.child("trials").child(self.key).remove()
        print("Delete successful")

    def get_flora(self):
        for device in self.devices:
            if device.name == 'Flora':
                return device
        raise Exception('Flora not found')

    def get_ground_truth(self):
        for device in self.devices:
            if device.name == 'USBUART':
                return device
        raise Exception('Ground truth not found')

    def dump_csv(self, filename):
        print("Outputting to file: " + filename)
        columns = ['red_led', 'ir_led']
        device = self.get_flora()
        device.convert_index_to(np.int64)
        device.df.to_csv(path_or_buf=filename, columns=columns, header=False, index=False)
        print("CSV file created")


def fetch_trials():
    trials = []
    trial_docs = db.child('trials').get()
    for trial_doc in trial_docs.each():
        trials.append(Trial(trial_doc))
    return trials
