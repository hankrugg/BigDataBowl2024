from typing import Tuple

import pandas as pd
import numpy as np
from pandas import DataFrame


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


def all_plays_left_to_right(plays: pd.DataFrame, tracking: pd.DataFrame) -> tuple[DataFrame, DataFrame]:
    # Define the pivot point for rotation
    pivot_x, pivot_y = 60, 26.65

    # Apply the 180-degree rotation transformation only for 'left' playDirection
    left_mask = tracking['playDirection'] == 'left'

    indices_left = tracking.index[left_mask].tolist()

    left_plays = tracking.iloc[indices_left]['playId'].unique()

    tracking.loc[left_mask, 'x'] = 2 * pivot_x - tracking.loc[left_mask, 'x']
    tracking.loc[left_mask, 'y'] = 2 * pivot_y - tracking.loc[left_mask, 'y']

    tracking.loc[left_mask, 'playDirection'] = 'right'

    plays['yardline_after_switching_direction'] = 0

    plays_mask = plays['playId'].isin(left_plays)

    plays.loc[plays_mask, 'yardline_after_switching_direction'] = 120 - plays.loc[plays_mask, 'absoluteYardlineNumber']

    plays = plays.drop(columns=['absoluteYardlineNumber'])
    plays = plays.rename(columns={'yardline_after_switching_direction': 'absoluteYardlineNumber'})

    return plays, tracking


if __name__ == "__main__":
    tracking = pd.read_csv("data/tracking_week_1.csv")

    tracking = create_acceleration_vectors(tracking)
    tracking = create_velocity_vectors(tracking)

    print(tracking.head())
