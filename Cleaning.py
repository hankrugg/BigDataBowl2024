"""

Created on Mon Jul 25 14:
@author: <NAME>

Cite: https://www.geeksforgeeks.org/handling-large-datasets-in-python/
"""
import pandas as pd
import numpy as np
from dateutil.parser import parse
from pandas import Series


# Combine all datasets into one master
def load_all_data(games: pd.DataFrame, plays: pd.DataFrame, tracking: pd.DataFrame,
                  players: pd.DataFrame, tackles: pd.DataFrame) -> pd.DataFrame:
    """
    Load all data
    :param games:
    :param plays:
    :param tracking:
    :param players:
    :param tackles:
    :return: all
    """
    df = pd.merge(games, plays, on='gameId', how='left')
    df = pd.merge(df, tracking, on='playId', how='left')
    df = pd.merge(df, players, on='nflId', how='left')
    df = pd.merge(df, tackles, on='nflId', how='left')

    return df


def clean_games_data(games: pd.DataFrame) -> pd.DataFrame:
    """
    Clean games data-- reduce memory usage by downcasting integers and changing date time
    :param games: Raw games dataset
    :return: Cleaned games dataset
    """
    memory_before = games.memory_usage().sum() / 1024

    # Ensure the specified columns are int
    games_columns_to_convert_to_int = ['gameId', 'season', 'week', 'homeFinalScore', 'visitorFinalScore']

    # Convert the specified columns to int32
    games[games_columns_to_convert_to_int] = games[games_columns_to_convert_to_int].astype('int32')

    # Handle the times
    games['gameDate'] = pd.to_datetime(games['gameDate'])
    games['gameTimeEastern'] = pd.to_datetime(games['gameTimeEastern'], format='%H:%M:%S').dt.time

    # There should be no NA values after cleaning
    memory_after = games.memory_usage().sum() / 1024

    print("Games data has been cleaned and memory has been reduced by " + str(memory_before - memory_after) + " bytes.")

    return games


def clean_plays_data(plays: pd.DataFrame) -> pd.DataFrame:
    """
    Clean games data-- reduce memory usage by downcasting integers and downcasting floats. Remove all plays that have been
    nullified by penalties since the play may be skewed by holding or some other penalty that might affect the tackle.
    :param plays: Raw plays dataset
    :return: Cleaned plays dataset
    """
    # There will be yardline side NAs for when the line of scrimmage is exactly on the 50 yard line
    # There are a few hundred plays where its registered as a pass but the passLength is NA, this is because
    # the play was designed to be a pass, but the quarterback scrambled and did not throw the ball

    # Keep track of the memory in kilobytes
    memory_before = plays.memory_usage().sum() / 1024

    # Drop all the plays that have been nullified by penalty because they players may play differently on these plays
    plays = plays.drop(plays[plays['playNullifiedByPenalty'] == 'Y'].index)

    # Drop the plays where the expectedPointsAdded is None
    plays = plays.drop(plays[plays['expectedPointsAdded'].isnull()].index)

    # Drop the plays where the defenders in the box is None
    plays = plays.drop(plays[plays['defendersInTheBox'].isnull()].index)

    # Columns to transform
    plays_columns_to_convert_to_int = ['gameId', 'playId', 'ballCarrierId', 'quarter', 'down', 'yardsToGo',
                                       'yardlineNumber', 'preSnapHomeScore', 'preSnapVisitorScore',
                                       'prePenaltyPlayResult', 'playResult', 'absoluteYardlineNumber']

    # Convert the specified columns to int32
    plays[plays_columns_to_convert_to_int] = plays[plays_columns_to_convert_to_int].astype('int32')

    # This constrains the floats to 7 digits which might affect the outcome and can be changed back to float64
    plays_columns_to_convert_to_float = ['passLength', 'penaltyYards', 'defendersInTheBox', 'passProbability',
                                         'preSnapHomeTeamWinProbability', 'preSnapVisitorTeamWinProbability',
                                         'homeTeamWinProbabilityAdded', 'visitorTeamWinProbilityAdded',
                                         'expectedPoints', 'expectedPointsAdded']
    plays[plays_columns_to_convert_to_float] = plays[plays_columns_to_convert_to_float].astype('float32')

    # AFTER CLEANING NA VALUES
    # yardlineSide 163
    # passResult 6225
    # passLength 6668
    # penaltyYards 11869
    # foulName1 11876
    # foulName2 12133
    # foulNFLId1 11876
    # foulNFLId2 12133
    # All other columns should have no NA values

    # Keep track of the memory in kilobytes
    memory_after = plays.memory_usage().sum() / 1024

    print("Plays data has been cleaned and memory has been reduced by " + str(memory_before - memory_after) + " bytes.")
    return plays


def clean_players_data(players: pd.DataFrame) -> pd.DataFrame:
    """
    Clean Players data-- reduce the memory usage, convert the heights to inches, and convert the birthdates
    into pandas datetime objects
    :param players: Raw players data
    :return: Cleaned players data
    """

    # Keep track of the memory in kilobytes
    memory_before = players.memory_usage().sum() / 1024

    # Columns to transform
    players_columns_to_convert_to_int = ['nflId', 'weight']
    players[players_columns_to_convert_to_int] = players[players_columns_to_convert_to_int].astype('int32')

    # Some of the birthdates are in a different format
    # Use the helper function to parse the date in regard to the different format, then convert it to pandas.datetime
    players['birthDate'] = pd.to_datetime(_parse_date_column(players['birthDate'])).dt.date

    # Fill the missing birthdates with the mode birthdate, could be changed but works since it is an
    # applicable birthdate and will be able to be calculated though the dates whereas median or mode won't
    players['birthDate'] = players['birthDate'].fillna(players['birthDate'].mode())

    # Convert the heights of the players from "6-2" (6 feet 2 inches) to int(74) (74 inches)
    players['height'] = _parse_height_column(players['height'])

    # Keep track of the memory in kilobytes
    memory_after = players.memory_usage().sum() / 1024

    print(
        "Players data has been cleaned and memory has been reduced by " + str(memory_before - memory_after) + " bytes.")

    return players


def _parse_date_column(date_column: Series) -> Series:
    """
    Helper function to parse the mixed dates in the dataframe column
    :param date_column: Pandas date series column to parse
    :return: Pandas Series with the correctly formatted dates
    """
    # Store the dates in a column
    dates = []
    for date in date_column:
        # The parse function used does not handle NA values, so we can only perform the
        # operation on non-null columns
        if pd.notnull(date):
            dates.append(parse(date))
        # Return a pandas series to be used as the modified column
    return pd.Series(dates)


def _parse_height_column(height_column: Series) -> Series:
    """
    Helper function to parse the height in the format 6-2 for 6 feet 2 inches
    :param height_column: Pandas height series column to parse
    :return: Pandas Series with the correctly formatted heights
    """
    # Store the heights in a column
    heights = []
    for height in height_column:
        height_in_inches = 0
        # Separate the height by the separator, "-"
        height_list = str(height).split(sep='-')
        # Add the feet in inches to the height
        # Assume that the feet of a
        height_in_inches += int(height_list[0]) * 12
        # Add the inches to the height
        height_in_inches += int(height_list[1])
        heights.append(height_in_inches)

    return pd.Series(heights)


def clean_tracking_data(tracking: pd.DataFrame) -> pd.DataFrame:
    """
    Clean Players data-- reduce the memory usage, convert the heights to inches, and convert the birthdates
    into pandas datetime objects
    :param tracking: Raw tracking data
    :return: Cleaned tracking data
    """
    # Keep track of memory in kilobytes
    memory_before = tracking.memory_usage().sum() / 1024

    # Columns to transform to int
    tracking_columns_to_convert_to_int = ['gameId', 'playId', 'frameId']
    tracking[tracking_columns_to_convert_to_int] = tracking[tracking_columns_to_convert_to_int].astype('int32')

    # Columns to transform to float
    tracking_columns_to_convert_to_float = ['x', 'y', 'a', 's', 'o', 'dir', 'dis']
    tracking[tracking_columns_to_convert_to_float] = tracking[tracking_columns_to_convert_to_float].astype('float32')

    # Make the time of the frame into a pandas datetime
    # Keep as both the date and time since the tracking data gives both the date and the time
    tracking['time'] = pd.to_datetime(tracking['time'])

    memory_after = tracking.memory_usage().sum() / 1024
    print("Tracking data has been cleaned and memory has been reduced by " + str(
        memory_before - memory_after) + " bytes.")

    return tracking


def clean_tackles_data(tackles: pd.DataFrame) -> pd.DataFrame:
    memory_before = tackles.memory_usage().sum() / 1024

    tackles_columns_to_convert_to_int = ['gameId', 'playId', 'nflId', 'tackle', 'assist', 'forcedFumble',
                                         'pff_missedTackle']
    tackles[tackles_columns_to_convert_to_int] = tackles[tackles_columns_to_convert_to_int].astype('int32')

    memory_after = tackles.memory_usage().sum() / 1024
    print(
        "Tackles data has been cleaned and memory has been reduced by " + str(memory_before - memory_after) + " bytes.")

    return tackles


# Remove duplicates


# Remove plays that don't have a snap of the ball


# Remove plays that don't have an end to the play


if __name__ == '__main__':
    games = pd.read_csv("data/games.csv")
    players = pd.read_csv("data/players.csv")
    plays = pd.read_csv("data/plays.csv")
    tackles = pd.read_csv("data/tackles.csv")

    tracking = []
    for i in range(1, 10):
        tracking.append(pd.read_csv(f"data/tracking_week_{i}.csv"))
    tracking = pd.concat(tracking)

    games = transform_games_data(games)
    plays = transform_plays_data(plays)
    players = transform_players_data(players)
    tracking = transform_tracking_data(tracking)
    tackles = transform_tackles_data(tackles)

    data = load_all_data(games, plays, tracking, players, tackles)
