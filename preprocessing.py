"""
Created on Mon Jul 29
@author: <Hank Rugg>

Influence based on paper by Javier Fernandez and Luke Bornn
https://static.capabiliaserver.com/frontend/clients/barca/wp_prod/wp-content/uploads/2018/05/Wide-Open-Spaces.pdf

Influence implementation based on spatial.py mpchang
https://github.com/mpchang/uncovering-missed-tackle-opportunities/blob/main/code/spatial.py
"""
import numpy as np
import pandas as pd


def create_acceleration_vectors(tracking: pd.DataFrame):
    """
    Creates acceleration vectors and their corresponding (x,y)  components for each frame in the tracking data
    :param tracking: Dataset of NFL player tracking data
    :return: Dataset with NFL player tracking data with acceleration components added to both x and y
    """
    tracking_copy = tracking.copy()
    # Convert direction from degrees to radians
    tracking_copy['dir_rad'] = np.radians(tracking_copy['dir'])

    # Calculate the acceleration vectors
    tracking_copy['x_acceleration_component'] = (tracking_copy['a'] * np.sin(tracking_copy['dir_rad']))
    tracking_copy['y_acceleration_component'] = (tracking_copy['a'] * np.cos(tracking_copy['dir_rad']))

    return tracking_copy


def create_velocity_vectors(tracking: pd.DataFrame):
    """
    Creates velocity vectors and their corresponding (x,y) components for each frame in the tracking data
    :param tracking: Dataset of NFL player tracking data
    :return: Dataset with NFL player tracking data with velocity components added to both x and y
    """
    tracking_copy = tracking.copy()

    # Convert direction from degrees to radians
    tracking_copy['dir_rad'] = np.radians(tracking_copy['dir'])

    # Calculate the change in position based on velocity
    tracking_copy['x_velocity_component'] = (tracking_copy['s'] * np.sin(tracking_copy['dir_rad']))
    tracking_copy['y_velocity_component'] = (tracking_copy['s'] * np.cos(tracking_copy['dir_rad']))

    return tracking_copy


def _calculate_influence(row):
    # Constants
    MAX_SPEED = 18
    INFLUENCE_RADIUS = 10

    # Calculate scaling factors
    sx = (INFLUENCE_RADIUS + (INFLUENCE_RADIUS * row['s_player']) / MAX_SPEED) / 2
    sy = (INFLUENCE_RADIUS - (INFLUENCE_RADIUS * row['s_player']) / MAX_SPEED) / 2

    # Create scaling and rotation matrices
    scaling = np.array([[sx, 0], [0, sy]])
    rotation = np.array([[np.cos(row['dir_rad_player']), -np.sin(row['dir_rad_player'])],
                         [np.sin(row['dir_rad_player']), np.cos(row['dir_rad_player'])]])

    # Covariance matrix
    cov = rotation @ scaling @ scaling @ rotation.T
    inv_cov = np.linalg.inv(cov)
    det_cov = np.linalg.det(cov)

    # Mean vector
    x = row['x_player'] + (np.cos(row['dir_rad_player']) * row['s_player'] * 0.5)
    y = row['y_player'] + (np.sin(row['dir_rad_player']) * row['s_player'] * 0.5)
    mean_vect = np.array([x, y])

    # Gaussian PDF calculation
    point = np.array([row['x_football'], row['y_football']])
    diff = point - mean_vect
    exponent = -0.5 * (diff.T @ inv_cov @ diff)
    norm_factor = 1 / (np.sqrt((2 * np.pi) ** len(mean_vect) * det_cov))
    gaussian_pdf = norm_factor * np.exp(exponent)

    return gaussian_pdf


def create_player_influence(tracking: pd.DataFrame) -> pd.DataFrame:
    """
    Computes the degree of influence for each player on the ball carrier.
    :param tracking: DataFrame containing the tracking data.
    :return: DataFrame with column for the degree of influence the player has on the ball
    """
    tracking_copy = tracking.copy()

    # Filter football tracking data
    football_tracking = tracking_copy.query("displayName == 'football'")

    # Merge football data with player data
    football_and_player_tracking = pd.merge(football_tracking, tracking_copy,
                                            on=['gameId', 'playId', 'frameId', 'time', 'playDirection'],
                                            suffixes=('_football', '_player'))

    # Apply influence calculation
    football_and_player_tracking['influence_degree'] = football_and_player_tracking.apply(_calculate_influence, axis=1)

    # "Unmerge" the columns to get rid of the redundant football data
    football_and_player_tracking = football_and_player_tracking.drop(columns=['nflId_football', 'displayName_football',
                                                                              'jerseyNumber_football', 'club_football',
                                                                              'x_football', 'y_football', 's_football',
                                                                              'a_football', 'dis_football',
                                                                              'o_football', 'dir_football',
                                                                              'event_football', 'dir_rad_football',
                                                                              'x_acceleration_component_football',
                                                                              'y_acceleration_component_football',
                                                                              'x_velocity_component_football',
                                                                              'y_velocity_component_football'])

    # Renaming columns to remove the _player suffix
    football_and_player_tracking = football_and_player_tracking.rename(columns={
        'nflId_player': 'nflId',
        'displayName_player': 'displayName',
        'jerseyNumber_player': 'jerseyNumber',
        'club_player': 'club',
        'x_player': 'x',
        'y_player': 'y',
        's_player': 's',
        'a_player': 'a',
        'dis_player': 'dis',
        'o_player': 'o',
        'dir_player': 'dir',
        'event_player': 'event',
        'dir_rad_player': 'dir_rad',
        'x_acceleration_component_player': 'x_acceleration_component',
        'y_acceleration_component_player': 'y_acceleration_component',
        'x_velocity_component_player': 'x_velocity_component',
        'y_velocity_component_player': 'y_velocity_component',
        'influence_degree_player': 'influence_degree'
    })

    return football_and_player_tracking


def create_distance_to_ball(tracking: pd.DataFrame) -> pd.DataFrame:
    """
    Creates distance from each player to the ball.
    :param tracking: DataFrame containing the tracking data.
    :return: DataFrame containing the tracking data with column added for the distance to the ball
    """
    tracking_copy = tracking.copy()

    football_tracking = tracking_copy.query("displayName == 'football'")

    # Merge football data with player data
    football_and_player_tracking = pd.merge(football_tracking, tracking_copy,
                                            on=['gameId', 'playId', 'frameId', 'time', 'playDirection'],
                                            suffixes=('_football', '_player'))
    # Calculate the distance from player to ball
    football_and_player_tracking['player_to_football_distance'] = np.sqrt(
        (football_and_player_tracking['x_player'] - football_and_player_tracking['x_football']) ** 2 + (
                football_and_player_tracking['y_player'] - football_and_player_tracking['y_football']) ** 2)

    # "Unmerge" the columns to get rid of the redundant football data
    football_and_player_tracking = football_and_player_tracking.drop(columns=['nflId_football', 'displayName_football',
                                                                              'jerseyNumber_football', 'club_football',
                                                                              'x_football', 'y_football', 's_football',
                                                                              'a_football', 'dis_football',
                                                                              'o_football', 'dir_football',
                                                                              'event_football', 'dir_rad_football',
                                                                              'x_acceleration_component_football',
                                                                              'y_acceleration_component_football',
                                                                              'x_velocity_component_football',
                                                                              'y_velocity_component_football'])

    # Renaming columns to remove the _player suffix
    football_and_player_tracking = football_and_player_tracking.rename(columns={
        'nflId_player': 'nflId',
        'displayName_player': 'displayName',
        'jerseyNumber_player': 'jerseyNumber',
        'club_player': 'club',
        'x_player': 'x',
        'y_player': 'y',
        's_player': 's',
        'a_player': 'a',
        'dis_player': 'dis',
        'o_player': 'o',
        'dir_player': 'dir',
        'event_player': 'event',
        'dir_rad_player': 'dir_rad',
        'x_acceleration_component_player': 'x_acceleration_component',
        'y_acceleration_component_player': 'y_acceleration_component',
        'x_velocity_component_player': 'x_velocity_component',
        'y_velocity_component_player': 'y_velocity_component'
    })

    return football_and_player_tracking


def all_plays_left_to_right(plays: pd.DataFrame, tracking: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Changes all plays that are going from left to right by changing the (x,y), acceleration, and velocity
    :param plays:
    :param tracking:
    :return:
    """
    plays_copy = plays.copy()
    tracking_copy = tracking.copy()

    # Define the pivot point for rotation
    pivot_x, pivot_y = 60, 26.65

    # Apply the 180-degree rotation transformation only for 'left' playDirection
    left_mask = tracking_copy['playDirection'] == 'left'

    # Rotate the plays (x, y) 180 degrees that are going right to left
    tracking_copy.loc[left_mask, 'x'] = 2 * pivot_x - tracking_copy.loc[left_mask, 'x']
    tracking_copy.loc[left_mask, 'y'] = 2 * pivot_y - tracking_copy.loc[left_mask, 'y']

    # Rotate the directions of each player 180 degrees and keep it between 0-360 degrees
    tracking_copy.loc[left_mask, 'dir'] = (tracking_copy.loc[left_mask, 'dir'] + 180) % 360
    tracking_copy.loc[left_mask, 'o'] = (tracking_copy.loc[left_mask, 'o'] + 180) % 360

    # Change the play direction to right
    tracking_copy.loc[left_mask, 'playDirection'] = 'right'

    # Update the yardline for plays where play direction is left
    left_plays = tracking_copy.loc[left_mask, ['gameId', 'playId']].drop_duplicates()
    plays_copy['yardline_after_switching_direction'] = plays_copy['absoluteYardlineNumber']
    for index, row in left_plays.iterrows():
        game_id = row['gameId']
        play_id = row['playId']
        play_mask = (plays_copy['gameId'] == game_id) & (plays_copy['playId'] == play_id)
        plays_copy.loc[play_mask, 'yardline_after_switching_direction'] = 120 - plays_copy.loc[
            play_mask, 'absoluteYardlineNumber']

    # Drop the old 'absoluteYardlineNumber' column and rename the new one
    plays_copy = plays_copy.drop(columns=['absoluteYardlineNumber'])
    plays_copy = plays_copy.rename(columns={'yardline_after_switching_direction': 'absoluteYardlineNumber'})

    return plays_copy, tracking_copy
