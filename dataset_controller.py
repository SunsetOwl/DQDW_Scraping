import h5py
import os.path
import datetime

import numpy as np
import pandas as pd


class DatasetController:
    """This class handles all interactions with the HDF5 Dataset."""

    database = h5py.Empty

    def __init__(self, filename, games):

        """Setup of the basic file information"""

        self.filename = filename
        self.games = games
        if not os.path.isfile(self.filename):
            self.setup()
        else:
            self.database = h5py.File(self.filename, "a")

    def setup(self):

        """Set up the base files with dummy datasets of length 1"""

        self.database = h5py.File(self.filename, "w")

        # Load the prepared files containing the exact plans for setting up the file
        groups_to_load = pd.read_csv("Sources/hdf5 groups.csv", header=0, index_col=0)
        datasets_to_load = pd.read_csv("Sources/hdf5 datasets.csv", header=0, index_col=0)

        # Set up the groups or 'filepaths' inside the HDF5-File
        for index, group in groups_to_load.iterrows():
            self.database.create_group(group["Path"])

        # Set up the datasets in the correct format
        for index, dataset in datasets_to_load.iterrows():
            group = self.database[dataset["Group"]]

            dt = h5py.string_dtype(encoding='utf-8')

            if dataset["Datatype"] == "Float":
                dt = np.dtype("float64")
            elif dataset["Datatype"] == "Integer":
                dt = np.dtype("int64")

            columns = dataset["Set Columns"]
            if dataset["Column per Game"]:
                columns = columns + self.games.shape[0]

            created_set = group.create_dataset(dataset["Name"], (1, columns), maxshape=(None, None), dtype=dt)
            created_set.attrs["Datatype"] = dataset["Datatype"]

            if dataset["Datetype"] == "Full":               # Only on the Logs, so String
                created_set.attrs["Dateformat"] = "%Y-%m-%d %H:%M:%S"
                created_set[0, 0] = datetime.datetime.now().strftime(created_set.attrs["Dateformat"])
                for i in range(1, columns):
                    created_set[0, i] = ""

            elif dataset["Datetype"] == "Date and Time":    # For the Hourly information, too long for one column
                created_set.attrs["Dateformat"] = ["%Y%m%d", "%H%M"]
                created_set[0, 0] = int(datetime.datetime.now().strftime(created_set.attrs["Dateformat"][0]))
                created_set[0, 1] = int(datetime.datetime.now().strftime(created_set.attrs["Dateformat"][1]))
                for i in range(2, columns):
                    created_set[0, i] = 0

            elif dataset["Datetype"] == "Date":             # For the Daily information
                created_set.attrs["Dateformat"] = "%Y%m%d"
                if dataset["Datatype"] == "String":
                    created_set[0, 0] = datetime.datetime.now().strftime(created_set.attrs["Dateformat"])
                    for i in range(1, columns):
                        created_set[0, i] = ""
                else:
                    created_set[0, 0] = int(datetime.datetime.now().strftime(created_set.attrs["Dateformat"]))
                    for i in range(1, columns):
                        created_set[0, i] = 0

            print(type(created_set.attrs["Dateformat"]))
            self.add_log(index + " (" + dataset["Source"] + ") - Setup Successful")

        self.add_log("Database Setup Successful")

    def add_log(self, message):
        """Add a log entry about what was just finished"""

        logs = self.database["logs/log_data"]
        logs.resize(logs.shape[0] + 1, axis=0)
        logs[-1, 0] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        logs[-1, 1] = message
        print(logs[-1, 1].decode("utf-8"))

    def add_scrape(self, file, new_data):
        """Add the measured data to the given dataset, if the dataset contains dummy value, replace it"""

        dataset = self.database[file]
        first_entry = False

        # Hourly Data needs to be handled differently to avoid doubled entries

        if type(dataset.attrs["Dateformat"]) is np.ndarray:
            log_type = "Hourly"
        else:
            log_type = "Daily"

        # Ensure that the first row in the dataset is actually used

        if dataset.shape[0] == 1:
            first_entry = not self.check_logs(file + " - Dummy Replaced")
            if not first_entry:
                dataset.resize(dataset.shape[0] + 1, axis=0)
        else:
            dataset.resize(dataset.shape[0] + 1, axis=0)

        if log_type == "Hourly":

            # Hourly Data arrives in the format:
            # [ [[Log times for game 1][Log times for game 2][...]] [[Counts for game 1][...]] ]

            for game in range(0, len(new_data[0])):

                found_index = 0
                found = False
                count = len(new_data[0][game])

                for log in range(0, count):
                    date = int(new_data[0][game][log].strftime(dataset.attrs["Dateformat"][0]))
                    time = int(new_data[0][game][log].strftime(dataset.attrs["Dateformat"][1]))

                    if date > 0:

                        # Check if the timeslot has a row already
                        if not first_entry:
                            found = False
                            for check in range(found_index, dataset.shape[0]):
                                if dataset[check, 0] == date and dataset[check, 1] == time:
                                    found_index = check
                                    found = True
                            if not found:
                                dataset.resize(dataset.shape[0] + 1, axis=0)

                        # Place into the row of the same time
                        if found:
                            insert_at = found_index
                        else:
                            insert_at = -1

                        dataset[insert_at, 0] = date
                        dataset[insert_at, 1] = time
                        dataset[insert_at, 2 + game] = new_data[1][game][log]

                        if first_entry:
                            self.add_log(file + " - Dummy Replaced")
                            first_entry = False

        else:

            # If the data isn't hourly, just add it, as daily data is only fetched once a day

            if dataset.attrs["Datatype"] == "String":
                dataset[-1, 0] = datetime.datetime.now().strftime(dataset.attrs["Dateformat"])
            else:
                dataset[-1, 0] = int(datetime.datetime.now().strftime(dataset.attrs["Dateformat"]))

            offset = 1

            for i in range(len(new_data)):
                dataset[-1, i + offset] = new_data[i]

            if first_entry:
                self.add_log(file + " - Dummy Replaced")

        self.add_log(file + " - Added Data Successfully")

    def check_logs(self, message, start="2024-01-01 00:00",
                   end=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")):
        """Checks the logs in a specific time range for a message e.g. 'completed' or 'failed'"""

        for [logged, log] in self.database["logs/log_data"]:
            if start <= logged.decode("utf-8") <= end and message in log.decode("utf-8"):
                return True

        return False

    def get_dataset_daily(self, file):

        gamedata_columns = ['Logged On']
        for game in self.games["Title"]:
            gamedata_columns.append(game)

        gamedata = pd.DataFrame(columns=gamedata_columns)

        dataset = self.database[file]

        for scrape in dataset:
            rating = [datetime.datetime.strptime(str(int(scrape[0])), dataset.attrs["Dateformat"])]
            for game in range(0, self.games.shape[0]):
                rating.append(scrape[game + 1])
            gamedata.loc[len(gamedata), gamedata.columns] = rating

        return gamedata

    def array_steam_counts(self):

        gamedata_columns = ['Logged On']
        for game in self.games["Title"]:
            gamedata_columns.append(game)

        gamedata = pd.DataFrame(columns=gamedata_columns)

        dataset = self.database["hourly/players/steam_charts"]

        for scrape in dataset:
            dateformat = dataset.attrs["Dateformat"][0] + dataset.attrs["Dateformat"][1]
            datestring = str(int(scrape[0]))

            if scrape[0] > 0:

                if len(str(int(scrape[1]))) < 4:
                    if len(str(int(scrape[1]))) < 3:
                        if len(str(int(scrape[1]))) < 2:
                            if int(scrape[1]) == 0:
                                datestring = datestring + "0000"
                            else:
                                datestring = datestring + "000" + str(int(scrape[1]))
                        else:
                            datestring = datestring + "00" + str(int(scrape[1]))
                    else:
                        datestring = datestring + "0" + str(int(scrape[1]))
                else:
                    datestring = datestring + str(int(scrape[1]))

                rating = [datetime.datetime.strptime(datestring, dateformat)]
                for game in range(0, self.games.shape[0]):
                    if scrape[game+2] == 0:
                        rating.append(np.nan)
                    else:
                        rating.append(scrape[game+2])
                gamedata.loc[len(gamedata), gamedata.columns] = rating

        return gamedata

    def close(self):
        """Close the database connection"""

        self.database.close()
