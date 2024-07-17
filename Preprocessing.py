import pandas as pd
import numpy as np


def create_acceleration_vectors(tracking: pd.DataFrame):

    # Convert direction to radians
    tracking['dir_rad'] = np.radians(tracking['dir'])

    # Calculate the acceleration vectors
    tracking['x_acceleration_component'] = (tracking['a'] * np.sin(tracking['dir_rad']))
    tracking['y_acceleration_component'] = (tracking['a'] * np.cos(tracking['dir_rad']))

    return tracking


def create_velocity_vectors(tracking: pd.DataFrame):
    # Convert direction to radians
    tracking['dir_rad'] = np.radians(tracking['dir'])

    # Calculate the change in position based on velocity
    tracking['x_velocity_component'] = (tracking['s'] * np.sin(tracking['dir_rad']))
    tracking['y_velocity_component'] = (tracking['s'] * np.cos(tracking['dir_rad']))

    return tracking

def make_all_plays_left_to_right(tracking: pd.DataFrame):

    return tracking


if __name__ == "__main__":
    tracking = pd.read_csv("data/tracking_week_1.csv")

    tracking = create_acceleration_vectors(tracking)
    tracking = create_velocity_vectors(tracking)

    print(tracking.head())
