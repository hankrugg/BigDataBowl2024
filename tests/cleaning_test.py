import time
import unittest

import pandas as pd
import numpy as np

import cleaning


class CleaningTests(unittest.TestCase):

    def setUp(self):
        self.create_good_tracking()

    def create_good_tracking(self):
        data = {"gameId": [33],
                "playId": [24],
                "nflId": [90234],
                "displayName": ["Hank Rugg"],
                "frameId": [90],
                "time": ["2022-09-08 20:35:59.799999"],
                "jerseyNumber": [55],
                "club": ["LA"],
                "playDirection": ["right"],
                "x": [51.56],
                "y": [23.86],
                "s": [0.86],
                "a": [1.25],
                "dis": [0.08],
                "o": [66.43],
                "dir": [89.88],
                "event": ["NA"]}

        self.good_tracking = pd.DataFrame(data)

    def create_bad_tracking(self):
        data = {"gameId": [],
                "playId": [24],
                "nflId": ["kdf"],
                "displayName": [0],
                "frameId": [90],
                "time": ["2022-09-08 20:35:59.799999"],
                "jerseyNumber": [55],
                "club": ["LA"],
                "playDirection": ["right"],
                "x": [51.56],
                "y": [23.86],
                "s": [0.86],
                "a": [1.25],
                "dis": [0.08],
                "o": [66.43],
                "dir": [89.88],
                "event": ["NA"]}

        self.good_tracking = pd.DataFrame(data)

    def test_clean_tracking_memory(self):
        data = self.good_tracking.copy()
        memoryBefore = data.memory_usage().sum()
        data = cleaning.clean_tracking_data(data)
        memoryAfter = data.memory_usage().sum()
        self.assertTrue(memoryBefore >= memoryAfter, "Memory before cleaning should be greater than or equal to "
                                                     "memory after cleaning.")

    def test_clean_tracking_int_conversions(self):
        data = self.good_tracking.copy()
        data = cleaning.clean_tracking_data(data)
        self.assertTrue(type(data['gameId'].iloc[0]) == np.int32,
                        "gameId should be an int, not {}.".format(type(data['gameId'].iloc[0])))

        self.assertTrue(type(data['playId'].iloc[0]) == np.int32,
                        "playId should be an int, not {}.".format(type(data['gameId'].iloc[0])))

        self.assertTrue(type(data['frameId'].iloc[0]) == np.int32,
                        "frameId should be an int, not {}.".format(type(data['gameId'].iloc[0])))

    def test_clean_tracking_float_conversions(self):
        data = self.good_tracking.copy()
        data = cleaning.clean_tracking_data(data)
        self.assertTrue(type(data['x'].iloc[0]) == np.float32,
                        "x should be a float, not {}.".format(type(data['x'].iloc[0])))

        self.assertTrue(type(data['y'].iloc[0]) == np.float32,
                        "y should be a float, not {}.".format(type(data['y'].iloc[0])))

        self.assertTrue(type(data['a'].iloc[0]) == np.float32,
                        "a should be a float, not {}.".format(type(data['a'].iloc[0])))

        self.assertTrue(type(data['s'].iloc[0]) == np.float32,
                        "s should be a float, not {}.".format(type(data['s'].iloc[0])))

        self.assertTrue(type(data['o'].iloc[0]) == np.float32,
                        "o should be a float, not {}.".format(type(data['o'].iloc[0])))

        self.assertTrue(type(data['dir'].iloc[0]) == np.float32,
                        "dir should be a float, not {}.".format(type(data['dir'].iloc[0])))

        self.assertTrue(type(data['dis'].iloc[0]) == np.float32,
                        "dis should be a float, not {}.".format(type(data['dis'].iloc[0])))

    def test_clean_tracking_time_conversions(self):
        data = self.good_tracking.copy()
        data = cleaning.clean_tracking_data(data)
        self.assertTrue(type(data['time'].iloc[0]) == pd._libs.tslibs.timestamps.Timestamp,
                        "time should be a pandas timestamp, not {}.".format(type(data['time'].iloc[0])))





    def test_clean_games_data(self):
        pass

    def test_clean_plays_data(self):
        pass

    def test_clean_players_data(self):
        pass

    def test_parse_date_column(self):
        pass

    def test_parse_height_column(self):
        pass

    def test_clean_tackles_data(self):
        pass

    def test_check_for_snap(self):
        pass

    def test_check_for_end(self):
        pass


if __name__ == '__main__':
    unittest.main()
