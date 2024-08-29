"""

Created on Mon Jul 25 14:
@author: <NAME>

Cite: https://www.geeksforgeeks.org/handling-large-datasets-in-python/
"""
import pandas as pd
from dateutil.parser import parse
from pandas import Series

from tqdm import tqdm


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


def check_for_missing_games_columns(games: pd.DataFrame) -> []:
    valid_columns = ['gameId', 'season', 'week', 'gameDate', 'gameTimeEastern',
                     'homeTeamAbbr', 'visitorTeamAbbr', 'homeFinalScore',
                     'visitorFinalScore']

    dataset_columns = games.columns

    missing_columns = []
    for column in valid_columns:
        if column not in dataset_columns:
            missing_columns.append(column)

    return missing_columns


def clean_games_data(games: pd.DataFrame) -> pd.DataFrame:
    """
    Clean games data-- reduce memory usage by downcasting integers and changing date time
    :param games: Raw games dataset
    :return: Cleaned games dataset
    """
    clean = True

    memory_before = games.memory_usage().sum() / 1024

    missing_columns = check_for_missing_games_columns(games)
    if len(missing_columns) > 0:
        clean = False
        print(f"The games dataset is missing the following columns: {missing_columns}.")

    # If there are any games with missing data, drop them
    games = games.dropna(subset=['gameId', 'homeTeamAbbr', 'visitorTeamAbbr', 'homeFinalScore', 'visitorFinalScore'])

    # If the date is wrong, correct it
    games['gameDate'] = pd.to_datetime(_parse_date_column(games['gameDate'])).dt.date

    # Ensure the specified columns are int
    games_columns_to_convert_to_int = ['gameId', 'season', 'week', 'homeFinalScore', 'visitorFinalScore']

    # Convert the specified columns to int32
    games[games_columns_to_convert_to_int] = games[games_columns_to_convert_to_int].astype('int32')

    # Handle the times
    games['gameDate'] = pd.to_datetime(games['gameDate'])
    games['gameTimeEastern'] = pd.to_datetime(games['gameTimeEastern'], format='%H:%M:%S').dt.time

    # There should be no NA values after cleaning
    memory_after = games.memory_usage().sum() / 1024

    if clean:
        print("Games data has been cleaned and memory has been reduced by " + str(
            memory_before - memory_after) + " bytes.")
    else:
        print("Cleaning the games data was attempted but there")

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
    plays = plays.drop(plays.query('playNullifiedByPenalty == "Y"').index)

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
    """
    Clean Tackles data-- reduce the memory by down casting ints
    :param tackles: Raw tackles dataset
    :return: Cleaned tackles dataset
    """
    # Keep track of memory in kilobytes
    memory_before = tackles.memory_usage().sum() / 1024

    # Columns to downcast
    tackles_columns_to_convert_to_int = ['gameId', 'playId', 'nflId', 'tackle', 'assist', 'forcedFumble',
                                         'pff_missedTackle']
    tackles[tackles_columns_to_convert_to_int] = tackles[tackles_columns_to_convert_to_int].astype('int32')

    memory_after = tackles.memory_usage().sum() / 1024
    print(
        "Tackles data has been cleaned and memory has been reduced by " + str(memory_before - memory_after) + " bytes.")

    return tackles


def check_for_snap(plays: pd.DataFrame, tracking: pd.DataFrame) -> pd.DataFrame:
    """
    Checks if the there is tracking data when the ball is snapped for each play. Returns a dataframe with
    plays without a snap removed
    :param plays: Dataframe containing plays
    :param tracking: Dataframe containing tracking data
    :return: Plays dataframe containing only plays that tracking starts before the snap of the ball
    """
    # Keep a list of the indices of invalid plays to then drop later
    invalid_plays = []

    # Iterate through all the game ids using tqdm which displays a progress bar
    gamesId = plays['gameId'].unique()
    for game in tqdm(gamesId):
        playsId = plays.query('gameId == @game')['playId'].unique()
        for play in playsId:
            # Retrieve the index from each game
            play_index = plays.query('gameId == @game and playId == @play').index.values[0]
            # Get the list of events that have occurred that play
            frame_events = tracking.query('gameId == @game and playId == @play')['event'].unique().tolist()
        if 'ball_snap' not in frame_events:
            print('gameId = ' + str(game) + ' playId = ' + str(play))
            # If a ball snap is not registered in the play events, this means that the player tracking
            # started after the ball was snapped. This is not a play we want to train on and therefore will be removed
            invalid_plays.append(play_index)
    final_plays = plays.drop(index=invalid_plays)
    print("Removed " + str(len(invalid_plays)) + " plays that do not have tracking at the snap of the ball.")
    return final_plays


def check_for_end(plays: pd.DataFrame, tracking: pd.DataFrame) -> pd.DataFrame:
    """
    Checks if the there is tracking data when the play ends for each play. Returns a dataframe with
    plays without the play end removed.
    :param plays: Dataframe containing plays
    :param tracking: Dataframe containing tracking data
    :return: Plays dataframe containing only plays that tracking ends after the play ends
    """
    # Keep a list of the indices of invalid plays to then drop later
    invalid_plays = []

    # Iterate through all the game ids using tqdm which displays a progress bar
    gamesId = plays['gameId'].unique()
    for game in tqdm(gamesId):
        playsId = plays.query('gameId == @game')['playId'].unique()
        for play in playsId:
            # Retrieve the index from each game
            play_index = plays.query('gameId == @game and playId == @play').index.values[0]
            # Get the list of events that have occurred that play
            frame_events = tracking.query('gameId == @game and playId == @play')['event'].unique().tolist()
        if 'tackle' not in frame_events or 'touchdown' not in frame_events or 'out_of_bounds' not in frame_events:
            # If a tackle, touchdown, or out_of_bounds is not registered in the play events, this means that the
            # player tracking ended before the play ended. This is not a play we want to train on and therefore
            # will be removed
            invalid_plays.append(play_index)
    final_plays = plays.drop(index=invalid_plays)
    print("Removed " + str(len(invalid_plays)) + " plays that do not have tracking for the end of the play.")
    return final_plays


def check_for_ball_carrier(plays: pd.DataFrame, tracking: pd.DataFrame) -> pd.DataFrame:
    """
    Checks if the ball carrier is in the tracking data.
    :param plays: Dataframe containing plays
    :param tracking: Dataframe containing tracking data
    :return: Plays dataframe containing only plays that the ball carrier is in the tracking data
    """
    # Keep a list of the indices of invalid plays to then drop later
    invalid_plays = []

    # Iterate through all the game ids using tqdm which displays a progress bar
    gamesId = plays['gameId'].unique()
    for game in tqdm(gamesId):
        playsId = plays.query('gameId == @game')['playId'].unique()
        for play in playsId:
            # Retrieve the index from each game
            play_index = plays.query('gameId == @game and playId == @play').index.values[0]
            # Get the list of events that have occurred that play
            frame_players = tracking.query('gameId == @game and playId == @play')['nflId'].unique().tolist()
            # Get the ball carrier for that play
            ball_carrier = plays.query('gameId == @game and playId == @play')['ballCarrierId'].unique()
            # If the ballCarrierId is not in the list of players, remove that play
            if ball_carrier not in frame_players:
                invalid_plays.append(play_index)

    final_plays = plays.drop(index=invalid_plays)
    print("Removed " + str(len(invalid_plays)) + " plays that do not have the ball carrier in the frames.")
    return final_plays

