import pandas as pd
import numpy as np

def create_acceleration_vectors(tracking: pd.DataFrame):
    if tracking.empty:
        print("No tracking data present")
        return pd.DataFrame()
    
    # Check for missing data in necessary columns
    if tracking['a'].isnull().all():
        print("No acceleration data present")
        return pd.DataFrame()
    if tracking['dir'].isnull().all():
        print("No direction data present")
        return pd.DataFrame()
    if tracking['x'].isnull().all():
        print("No x data present")
        return pd.DataFrame()
    if tracking['y'].isnull().all():
        print("No y data present")
        return pd.DataFrame()

    tracking['dir_rad'] = np.radians(tracking['dir'])

    # Calculate the acceleration vectors
    tracking['x2_acceleration'] = tracking['x'] + (tracking['a'] * np.cos(tracking['dir_rad']))
    tracking['y2_acceleration'] = tracking['y'] + (tracking['a'] * np.sin(tracking['dir_rad']))

    return tracking


def create_velocity_vectors(tracking: pd.DataFrame):
    if tracking.empty:
        print("No tracking data present")
        return pd.DataFrame()

    # Check for missing data in necessary columns
    if tracking['s'].isnull().all():
        print("No velocity data present")
        return pd.DataFrame()
    if tracking['dir'].isnull().all():
        print("No direction data present")
        return pd.DataFrame()
    if tracking['x'].isnull().all():
        print("No x data present")
        return pd.DataFrame()
    if tracking['y'].isnull().all():
        print("No y data present")
        return pd.DataFrame()

    # Convert direction to radians
    tracking['dir_rad'] = np.radians(tracking['dir'])

    # Calculate the change in position based on velocity
    tracking['x2_velocity'] = tracking['x'] + (tracking['s'] * np.cos(tracking['dir_rad']))
    tracking['y2_velocity'] = tracking['y'] + (tracking['s'] * np.sin(tracking['dir_rad']))

    return tracking


if __name__ == "__main__":
    tracking = pd.read_csv("data/tracking_week_1.csv")

    tracking = create_acceleration_vectors(tracking)

    tracking = create_velocity_vectors(tracking)
