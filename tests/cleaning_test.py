import unittest

import pandas as pd


class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.tracking = pd.read_csv('tests/testing_data/bad_tracking_data_week_1.csv')

    def __init__(self):
        super().__init__()
        self.setUp()

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

    def test_clean_tracking_data(self):
        pass

    def test_clean_tackles_data(self):
        pass

    def test_check_for_snap(self):
        pass

    def test_check_for_end(self):
        pass


if __name__ == '__main__':
    unittest.main()
